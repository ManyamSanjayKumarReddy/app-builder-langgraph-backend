from agent_v1.runtime.docker_manager import docker_manager, DockerError
from agent_v1.runtime.repository import RuntimeRepository


async def reconcile_runtimes_on_startup():
    """
    Reconcile DB runtime state with actual Docker containers.

    Rules:
    - DB is the source of truth
    - Docker state is authoritative for running/stopped
    - This function must NEVER crash app startup
    """
    repo = RuntimeRepository()
    runtimes = await repo.list_all()

    for runtime in runtimes:
        try:
            exists = docker_manager.container_exists(runtime.container_name)
            running = (
                docker_manager.is_running(runtime.container_name)
                if exists
                else False
            )

            status = "running" if running else "stopped"

            if runtime.status != status:
                await repo.update_status(runtime.project_name, status)

        except DockerError as e:
            # Do not block app startup due to Docker issues
            # Log and continue
            print(
                f"[RECONCILE_WARNING] "
                f"project={runtime.project_name} "
                f"error={e}"
            )
