"""
Purpose:
--------
HTTP + WebSocket API for runtime management.

Design Philosophy:
------------------
- Backend manages ONLY Docker container lifecycle.
- Application processes (Flask / FastAPI / Streamlit / agents)
  are user-controlled via WebSocket terminal.
- No backend-level process state is tracked.

Exposes:
---------
- Start container
- Stop container
- Delete container
- Get container runtime status
- WebSocket terminal (xterm.js)
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
import asyncio
from pydantic import BaseModel
from typing import Optional

from agent_v1.runtime.docker_manager import docker_manager, DockerError
from agent_v1.runtime.repository import RuntimeRepository, RuntimeNotFound
from agent_v1.runtime.terminal_manager import terminal_manager
from agent_v1.api.project_utils import resolve_project_dir

router = APIRouter(prefix="/projects", tags=["runtime"])
repo = RuntimeRepository()


# -------------------------------------------------------------------
# Response Models
# -------------------------------------------------------------------

class StartRuntimeResponse(BaseModel):
    project_name: str
    status: str
    container_id: str
    image: str


class RuntimeStatusResponse(BaseModel):
    project_name: str
    container_status: str
    container_id: Optional[str]
    image: str


# -------------------------------------------------------------------
# Container Lifecycle
# -------------------------------------------------------------------

@router.post("/{project_name}/runtime/start", response_model=StartRuntimeResponse)
async def start_runtime(project_name: str):
    """
    Create (if needed) and start the Docker container for a project.

    Behavior:
    - Validates project exists on disk
    - Creates container + DB record if missing
    - Starts container (idempotent)
    """
    try:
        resolve_project_dir(project_name)

        try:
            runtime = await repo.get(project_name)
        except RuntimeNotFound:
            await docker_manager.create_container(project_name)
            runtime = await repo.get(project_name)

        await docker_manager.start_container(project_name)
        runtime = await repo.get(project_name)

        return StartRuntimeResponse(
            project_name=runtime.project_name,
            status=runtime.status,
            container_id=runtime.container_name,
            image=runtime.image,
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Project not found: {project_name}",
        )
    except DockerError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_name}/runtime/status", response_model=RuntimeStatusResponse)
async def runtime_status(project_name: str):
    """
    Returns the current container runtime status.

    This is the single source of truth for the UI.
    """
    try:
        r = await repo.get(project_name)

        return RuntimeStatusResponse(
            project_name=r.project_name,
            container_status=r.status,
            container_id=r.container_name,
            image=r.image,
        )

    except RuntimeNotFound:
        raise HTTPException(
            status_code=404,
            detail=f"No runtime found for project: {project_name}",
        )


@router.post("/{project_name}/runtime/stop")
async def stop_runtime(project_name: str):
    """
    Stop the Docker container.

    Notes:
    - Safe to call even if container is already stopped
    - Terminal session (if any) will be closed automatically
    """
    try:
        await docker_manager.stop_container(project_name)
        terminal_manager.close(project_name)
        return {"status": "stopped"}

    except RuntimeNotFound:
        raise HTTPException(
            status_code=404,
            detail=f"No runtime found for project: {project_name}",
        )


@router.delete("/{project_name}/runtime")
async def delete_runtime(project_name: str):
    """
    Remove the Docker container and delete the runtime record.

    This is a destructive operation.
    """
    try:
        terminal_manager.close(project_name)
        await docker_manager.remove_container(project_name)
        return {"status": "deleted"}

    except RuntimeNotFound:
        raise HTTPException(
            status_code=404,
            detail=f"No runtime found for project: {project_name}",
        )


# -------------------------------------------------------------------
# WebSocket Terminal
# -------------------------------------------------------------------
@router.websocket("/{project_name}/runtime/ws/terminal")
async def runtime_terminal_ws(websocket: WebSocket, project_name: str):
    await websocket.accept()

    runtime = await repo.get(project_name)
    if runtime.status != "running":
        await websocket.send_text("Container not running")
        return  # FastAPI will close socket

    session = terminal_manager.get_or_create(
        project_name,
        runtime.container_name,
    )

    async def push_output():
        while True:
            data = session.read()
            if data:
                await websocket.send_text(data)
            await asyncio.sleep(0.01)

    task = asyncio.create_task(push_output())

    try:
        while True:
            msg = await websocket.receive_text()
            session.write(msg)

    except WebSocketDisconnect:
        pass

    finally:
        terminal_manager.close(project_name)
        task.cancel()
