import subprocess
from typing import Optional, Dict

from agent_v1.api.project_utils import resolve_project_dir
from agent_v1.runtime.repository import RuntimeRepository, RuntimeNotFound


class DockerError(Exception):
    pass


class DockerManager:
    """
    Docker lifecycle manager.
    Async-safe. DB is the source of truth.
    """

    DEFAULT_IMAGE = "python:3.11-slim"
    WORKDIR = "/workspace"

    def __init__(self):
        self.repo = RuntimeRepository()

    def _run(self, args: list[str]) -> str:
        try:
            result = subprocess.run(
                ["docker", *args],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise DockerError(e.stderr.strip() or str(e))

    # -------------------------
    # Docker inspection
    # -------------------------

    def container_exists(self, name: str) -> bool:
        return self._run(
            ["ps", "-a", "--filter", f"name=^{name}$", "--format", "{{.Names}}"]
        ) == name

    def is_running(self, name: str) -> bool:
        return self._run(
            ["ps", "--filter", f"name=^{name}$", "--format", "{{.Names}}"]
        ) == name

    # -------------------------
    # Lifecycle
    # -------------------------

    async def create_container(
        self,
        project_name: str,
        image: Optional[str] = None,
        ports: Optional[Dict[int, int]] = None,
    ):
        project_dir = resolve_project_dir(project_name)
        image = image or self.DEFAULT_IMAGE
        container_name = f"ai_builder_{project_name}"

        await self.repo.create(
            project_name=project_name,
            project_root=str(project_dir),
            image=image,
            container_name=container_name,
        )

        args = [
            "create",
            "--name", container_name,
            "-w", self.WORKDIR,
            "-v", f"{project_dir}:{self.WORKDIR}",
            image,
            "sleep", "infinity",
        ]

        self._run(args)

    async def start_container(self, project_name: str):
        runtime = await self.repo.get(project_name)

        if self.is_running(runtime.container_name):
            return

        self._run(["start", runtime.container_name])

        await self.repo.update_status(project_name, "running")

    async def stop_container(self, project_name: str):
        runtime = await self.repo.get(project_name)

        if self.is_running(runtime.container_name):
            self._run(["stop", runtime.container_name])
            await self.repo.update_status(project_name, "stopped")

    async def remove_container(self, project_name: str):
        runtime = await self.repo.get(project_name)

        if self.container_exists(runtime.container_name):
            if self.is_running(runtime.container_name):
                self._run(["stop", runtime.container_name])
            self._run(["rm", runtime.container_name])

        await self.repo.delete(project_name)


docker_manager = DockerManager()
