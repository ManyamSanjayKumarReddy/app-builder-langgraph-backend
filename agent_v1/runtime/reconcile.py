"""
Purpose:
--------
Reconciles persisted runtime state with actual Docker container state
during application startup.

Why this exists:
----------------
- Database is the source of truth for *known* runtimes
- Docker is the source of truth for *actual* container state
- Backend may crash or restart while containers are still running

This reconciliation ensures:
-----------------------------
- DB status reflects real container state
- UI receives correct runtime status after backend restart

Execution:
----------
- Runs ONCE during application startup
- Must NEVER crash application startup
"""

from agent_v1.runtime.docker_manager import docker_manager, DockerError
from agent_v1.runtime.repository import RuntimeRepository


async def reconcile_runtimes_on_startup():
    """
    Sync database runtime status with Docker container state.

    Rules:
    ------
    - If container exists AND is running → status = "running"
    - Otherwise → status = "stopped"
    - Missing containers are treated as stopped
    - Errors MUST NOT block app startup
    """
    repo = RuntimeRepository()

    # Fetch all known runtimes from DB
    runtimes = await repo.list_all()

    for runtime in runtimes:
        try:
            # Check Docker state
            exists = docker_manager.container_exists(
                runtime.container_name
            )

            running = (
                docker_manager.is_running(runtime.container_name)
                if exists
                else False
            )

            new_status = "running" if running else "stopped"

            # Update DB only if state differs
            if runtime.status != new_status:
                await repo.update_status(
                    runtime.project_name,
                    new_status,
                )

        except DockerError as e:
            # IMPORTANT:
            # Docker errors must never prevent app startup.
            # Log and continue safely.
            print(
                f"[RECONCILE_WARNING] "
                f"project={runtime.project_name} "
                f"error={e}"
            )
