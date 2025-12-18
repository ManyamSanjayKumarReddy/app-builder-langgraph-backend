"""
Purpose:
--------
Manages Docker container lifecycle for each generated project.

Design Philosophy:
------------------
- This module is the SINGLE authority for Docker container lifecycle.
- Backend manages containers, NOT application processes.
- Application execution happens exclusively via WebSocket terminal.

Responsibilities:
-----------------
- Create Docker containers with resource limits
- Start, stop, and remove containers
- Persist container lifecycle state in the database

Explicitly DOES NOT:
--------------------
- Execute application commands
- Manage processes inside containers
- Handle terminals or WebSockets
- Track application runtime state
"""

import subprocess
import asyncio
from typing import Optional

from agent_v1.api.project_utils import resolve_project_dir
from agent_v1.runtime.repository import RuntimeRepository


class DockerError(Exception):
    """
    Raised when a Docker CLI operation fails.

    This exception should be caught at the API layer
    and translated into an HTTP error response.
    """
    pass


class DockerManager:
    """
    Docker container lifecycle manager.

    One Docker container is created per project and kept
    alive using a long-running `sleep infinity` process.
    """

    DEFAULT_IMAGE = "python:3.11-slim"
    WORKDIR = "/workspace"

    def __init__(self):
        # Database-backed runtime repository
        self.repo = RuntimeRepository()

    # ------------------------------------------------------------------
    # Low-level Docker execution helpers
    # ------------------------------------------------------------------

    def _run(self, args: list[str]) -> str:
        """
        Execute a Docker CLI command synchronously.

        Args:
            args: List of Docker arguments (without 'docker')

        Returns:
            stdout output as string

        Raises:
            DockerError if command execution fails
        """
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

    async def _run_async(self, args: list[str]) -> str:
        """
        Execute a Docker CLI command asynchronously.

        Docker operations are blocking; this offloads them
        to a background thread to avoid blocking the event loop.
        """
        return await asyncio.to_thread(self._run, args)

    # ------------------------------------------------------------------
    # Docker state inspection
    # ------------------------------------------------------------------

    def container_exists(self, name: str) -> bool:
        """
        Check if a container exists (running or stopped).
        """
        return self._run(
            ["ps", "-a", "--filter", f"name=^{name}$", "--format", "{{.Names}}"]
        ) == name

    def is_running(self, name: str) -> bool:
        """
        Check if a container is currently running.
        """
        return self._run(
            ["ps", "--filter", f"name=^{name}$", "--format", "{{.Names}}"]
        ) == name

    # ------------------------------------------------------------------
    # Container lifecycle operations
    # ------------------------------------------------------------------

    async def create_container(
        self,
        project_name: str,
        image: Optional[str] = None,
    ):
        """
        Create a Docker container for a project.

        Behavior:
        ---------
        - Validates project directory exists
        - Persists runtime metadata in DB
        - Creates container in stopped state
        - Container runs `sleep infinity` to stay alive

        Notes:
        ------
        - Does NOT start the container
        - Safe to call only once per project
        """
        project_dir = resolve_project_dir(project_name)
        image = image or self.DEFAULT_IMAGE
        container_name = f"ai_builder_{project_name}"

        # Persist runtime metadata first (DB is source of truth)
        await self.repo.create(
            project_name=project_name,
            project_root=str(project_dir),
            image=image,
            container_name=container_name,
        )

        # Create container (but do not start)
        await self._run_async([
            "create",
            "--name", container_name,
            "--memory", "2g",
            "--cpus", "2.0",
            "-w", self.WORKDIR,
            "-v", f"{project_dir}:{self.WORKDIR}",
            image,
            "sleep", "infinity",
        ])

    async def start_container(self, project_name: str):
        """
        Start the Docker container for a project.

        This operation is idempotent.
        """
        runtime = await self.repo.get(project_name)

        if self.is_running(runtime.container_name):
            return

        await self._run_async(["start", runtime.container_name])
        await self.repo.update_status(project_name, "running")

    async def stop_container(self, project_name: str):
        """
        Stop the Docker container for a project.

        This does NOT delete the container.
        """
        runtime = await self.repo.get(project_name)

        if self.is_running(runtime.container_name):
            await self._run_async(["stop", runtime.container_name])
            await self.repo.update_status(project_name, "stopped")

    async def remove_container(self, project_name: str):
        """
        Remove the Docker container and delete runtime metadata.

        This is a destructive operation.
        """
        runtime = await self.repo.get(project_name)

        if self.container_exists(runtime.container_name):
            if self.is_running(runtime.container_name):
                await self._run_async(["stop", runtime.container_name])
            await self._run_async(["rm", runtime.container_name])

        # Remove DB record last
        await self.repo.delete(project_name)


# Singleton instance used across the application
docker_manager = DockerManager()
