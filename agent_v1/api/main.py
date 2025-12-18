from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse

from tortoise import Tortoise

from agent_v1.graph.graph import run_agent
from agent_v1.api.schemas import (
    GenerateProjectRequest,
    GenerateProjectResponse,
    ListFilesResponse,
    ReadFileResponse,
)
from agent_v1.api.project_utils import resolve_project_dir, GENERATED_PROJECTS_ROOT
from agent_v1.tools.filesystem import set_project_root, list_files, read_file
from agent_v1.api.runtime_routes import router as runtime_router
from agent_v1.api.db.config import init_db
from agent_v1.runtime.reconcile import reconcile_runtimes_on_startup
from agent_v1.runtime.terminal_manager import terminal_manager
from agent_v1.core.logging import setup_logging
from agent_v1.core.middleware import request_id_middleware
from agent_v1.runtime.command_policy import CommandRejected

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------

setup_logging()

# -------------------------------------------------------------------
# Application Lifespan
# -------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.

    Startup:
    - Initialize database
    - Reconcile DB runtime state with Docker

    Shutdown:
    - Close active terminal sessions
    - Close database connections
    """
    # 🔥 Initialize DB and bind models
    await init_db()

    # 🔥 Sync runtime DB state with Docker
    await reconcile_runtimes_on_startup()

    yield

    # 🔻 Shutdown cleanup
    terminal_manager.sessions.clear()
    await Tortoise.close_connections()

# -------------------------------------------------------------------
# FastAPI App
# -------------------------------------------------------------------

app = FastAPI(
    title="AI Project Builder API",
    version="1.0.0",
    lifespan=lifespan,
)

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_id_middleware)

# -------------------------------------------------------------------
# Routers
# -------------------------------------------------------------------

app.include_router(runtime_router)

# -------------------------------------------------------------------
# Health & Readiness
# -------------------------------------------------------------------

@app.get("/ready")
async def readiness_check():
    """
    Readiness probe:
    - Confirms DB connectivity
    """
    try:
        await Tortoise.get_connection("default").execute_query("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}


@app.get("/health")
def health_check():
    """
    Liveness probe.
    """
    return {
        "status": "ok",
        "service": "AI Project Builder API",
        "version": "1.0.0",
    }

# -------------------------------------------------------------------
# Project Management
# -------------------------------------------------------------------

@app.get("/projects", response_model=list[str])
def list_all_projects():
    """
    List all generated projects on disk.
    """
    if not GENERATED_PROJECTS_ROOT.exists():
        return []

    return sorted(
        p.name for p in GENERATED_PROJECTS_ROOT.iterdir() if p.is_dir()
    )


@app.post("/projects/generate", response_model=GenerateProjectResponse)
def generate_project(req: GenerateProjectRequest):
    """
    Generate a new project using the agent pipeline.
    """
    result = run_agent(req.prompt)

    coder_state = result.get("coder_state")
    if not coder_state:
        raise HTTPException(status_code=500, detail="Project generation failed")

    project_root = coder_state.project_root
    project_name = project_root.split("/")[-1]

    return GenerateProjectResponse(
        project_name=project_name,
        project_root=project_root,
    )

# -------------------------------------------------------------------
# File System APIs (Read-Only)
# -------------------------------------------------------------------

@app.get(
    "/projects/{project_name}/files",
    response_model=ListFilesResponse,
)
def list_project_files(project_name: str):
    """
    List files inside a generated project.
    """
    project_dir = resolve_project_dir(project_name)
    set_project_root(str(project_dir))

    files_output = list_files.run(".")
    files = (
        files_output.split("\n")
        if files_output and "No files found" not in files_output
        else []
    )

    return ListFilesResponse(
        project_name=project_name,
        files=files,
    )


@app.get(
    "/projects/{project_name}/files/read",
    response_model=ReadFileResponse,
)
def read_project_file(project_name: str, file_path: str):
    """
    Read a specific file from a project.
    """
    project_dir = resolve_project_dir(project_name)
    set_project_root(str(project_dir))

    content = read_file.run(file_path)
    if content.startswith("ERROR"):
        raise HTTPException(status_code=400, detail=content)

    return ReadFileResponse(
        project_name=project_name,
        file_path=file_path,
        content=content,
    )

# -------------------------------------------------------------------
# Exception Handling
# -------------------------------------------------------------------

@app.exception_handler(CommandRejected)
async def command_rejected_handler(_, exc: CommandRejected):
    """
    Handles rejected REST-based commands.
    (Not used by WebSocket terminals)
    """
    return JSONResponse(
        status_code=422,
        content={
            "error": "command_rejected",
            "detail": str(exc),
        },
    )
