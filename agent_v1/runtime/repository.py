"""
Purpose:
--------
Database access layer for container runtime state.

Design Principles:
------------------
- Database is the single source of truth for *container lifecycle*
- Backend tracks ONLY what it controls
- Application processes are NOT tracked here

What this repository manages:
------------------------------
- Container existence
- Container running / stopped status
- Container metadata (image, name, project root)
- Last executed command (optional, informational)

What this repository deliberately DOES NOT manage:
--------------------------------------------------
- Application process state (Flask, FastAPI, Streamlit, etc.)
- Runtime logs
- Terminal activity

Rationale:
----------
Process execution is handled exclusively via WebSocket terminal.
Tracking process state in DB would be inaccurate and misleading.
"""

from typing import List
from tortoise.exceptions import DoesNotExist

from agent_v1.api.db.models import ProjectRuntime


class RuntimeNotFound(Exception):
    """
    Raised when a runtime entry does not exist in the database.
    """
    pass


class RuntimeRepository:
    """
    Repository for ProjectRuntime persistence.

    This class abstracts all database access for runtime state
    and enforces a clean, container-only model.
    """

    # ------------------------------------------------------------------
    # Create / Read
    # ------------------------------------------------------------------

    async def create(
        self,
        project_name: str,
        project_root: str,
        image: str,
        container_name: str,
    ) -> ProjectRuntime:
        """
        Create a new runtime entry for a project.

        Containers are created in a STOPPED state by default.
        """
        return await ProjectRuntime.create(
            project_name=project_name,
            project_root=project_root,
            image=image,
            container_name=container_name,
            status="stopped",
        )

    async def get(self, project_name: str) -> ProjectRuntime:
        """
        Fetch runtime metadata for a project.
        """
        try:
            return await ProjectRuntime.get(project_name=project_name)
        except DoesNotExist:
            raise RuntimeNotFound(
                f"No runtime found for project: {project_name}"
            )

    async def list_all(self) -> List[ProjectRuntime]:
        """
        List all known runtimes.
        """
        return await ProjectRuntime.all()

    # ------------------------------------------------------------------
    # Container lifecycle updates
    # ------------------------------------------------------------------

    async def update_status(self, project_name: str, status: str) -> None:
        """
        Update container status (running / stopped).
        """
        updated = await ProjectRuntime.filter(
            project_name=project_name
        ).update(status=status)

        if not updated:
            raise RuntimeNotFound(project_name)

    async def update_last_command(
        self,
        project_name: str,
        command: str,
    ) -> None:
        """
        Persist the last executed command.

        This is informational only and not used for state tracking.
        """
        updated = await ProjectRuntime.filter(
            project_name=project_name
        ).update(last_command=command)

        if not updated:
            raise RuntimeNotFound(project_name)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete(self, project_name: str) -> None:
        """
        Delete runtime metadata after container removal.
        """
        deleted = await ProjectRuntime.filter(
            project_name=project_name
        ).delete()

        if not deleted:
            raise RuntimeNotFound(project_name)
