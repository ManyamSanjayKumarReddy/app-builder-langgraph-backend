from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

from agent_v1.runtime.docker_manager import docker_manager, DockerError
from agent_v1.runtime.executer import command_executor, ExecutionError
from agent_v1.runtime.repository import RuntimeRepository, RuntimeNotFound
from agent_v1.runtime.command_policy import validate_command
from agent_v1.runtime.process_manager import (
    process_manager,
    ProcessAlreadyRunning,
)
from agent_v1.api.project_utils import resolve_project_dir

router = APIRouter(prefix="/projects", tags=["runtime"])

repo = RuntimeRepository()

# -----------------------------
# Request / Response Models
# -----------------------------

class StartRuntimeResponse(BaseModel):
    project_name: str
    status: str
    container_id: str
    image: str


class ExecCommandRequest(BaseModel):
    command: str = Field(..., example="npm")
    args: List[str] = Field(default_factory=list, example=["run", "dev"])
    cwd: Optional[str] = Field(default=".")
    timeout: Optional[int] = Field(default=60)


class ExecCommandResponse(BaseModel):
    return_code: int
    stdout: str
    stderr: str


class RunProcessRequest(BaseModel):
    command: str = Field(..., example="npm")
    args: List[str] = Field(default_factory=list, example=["run", "dev"])
    cwd: Optional[str] = Field(default=".")
    env: Optional[Dict[str, str]] = None


class RuntimeStatusResponse(BaseModel):
    project_name: str
    status: str
    container_id: Optional[str]
    image: str
    last_command: Optional[str]

# Routes
@router.post(
    "/{project_name}/runtime/start",
    response_model=StartRuntimeResponse
)
async def start_runtime(project_name: str):
    try:
        resolve_project_dir(project_name)
        container_name = f"ai_builder_{project_name}"

        try:
            runtime = await repo.get(project_name)
        except RuntimeNotFound:
            if docker_manager.container_exists(container_name):
                runtime = await repo.create(
                    project_name=project_name,
                    project_root=str(resolve_project_dir(project_name)),
                    image=docker_manager.DEFAULT_IMAGE,
                    container_name=container_name,
                )
            else:
                await docker_manager.create_container(project_name)

        await docker_manager.start_container(project_name)

        runtime = await repo.get(project_name)

        return StartRuntimeResponse(
            project_name=runtime.project_name,
            status=runtime.status,
            container_id=runtime.container_name,
            image=runtime.image,
        )

    except DockerError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/{project_name}/runtime/exec",
    response_model=ExecCommandResponse
)
async def exec_command(project_name: str, req: ExecCommandRequest):
    try:
        code, stdout, stderr = await command_executor.exec(
            project_name=project_name,
            command=req.command,
            args=req.args,
            cwd=req.cwd,
            timeout=req.timeout,
        )

        return ExecCommandResponse(
            return_code=code,
            stdout=stdout,
            stderr=stderr,
        )

    except ExecutionError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/{project_name}/runtime/run"
)
async def run_long_process(project_name: str, req: RunProcessRequest):
    """
    Starts a long-running process (one per project).
    Output is streamed via WebSocket.
    """
    try:
        runtime = await repo.get(project_name)

        if runtime.status != "running":
            raise HTTPException(
                status_code=400,
                detail="Runtime is not running",
            )

        # Validate command
        validate_command(req.command, req.args, req.cwd)

        process_manager.start_process(
            project_name=project_name,
            container_name=runtime.container_name,
            command=req.command,
            args=req.args,
            cwd=req.cwd,
            env=req.env,
        )
        await repo.update_process_status(project_name, "running")

        return {
            "status": "started",
            "project_name": project_name,
            "command": " ".join([req.command] + req.args),
        }

    except RuntimeNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ProcessAlreadyRunning as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{project_name}/runtime/stop"
)
async def stop_runtime(project_name: str):
    """
    Stops the project's runtime container.
    """
    try:
        docker_manager.stop_container(project_name)
        return {"status": "stopped"}

    except (DockerError, RuntimeNotFound) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{project_name}/runtime"
)
async def remove_runtime(project_name: str):
    """
    Removes the runtime container and deletes DB record.
    """
    try:
        docker_manager.remove_container(project_name)
        return {"status": "removed"}

    except (DockerError, RuntimeNotFound) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{project_name}/runtime/status",
    response_model=RuntimeStatusResponse
)
async def runtime_status(project_name: str):
    """
    Returns runtime status for the project (DB-backed).
    """
    try:
        runtime = await repo.get(project_name)

        return RuntimeStatusResponse(
            project_name=runtime.project_name,
            status=runtime.status,
            container_id=runtime.container_name,
            image=runtime.image,
            last_command=runtime.last_command,
        )

    except RuntimeNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post(
    "/{project_name}/runtime/stop-process"
)
async def stop_process(project_name: str):
    """
    Stops the running process inside the container.
    """
    try:
        if not process_manager.has_process(project_name):
            raise HTTPException(
                status_code=404,
                detail="No running process found",
            )

        process_manager.stop_process(project_name)
        await repo.update_process_status(project_name, "stopped")

        return {
            "status": "process_stopped",
            "project_name": project_name,
        }

    except RuntimeNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
