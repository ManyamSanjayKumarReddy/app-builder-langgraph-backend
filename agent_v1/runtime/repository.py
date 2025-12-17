from typing import List
from tortoise.exceptions import DoesNotExist

from agent_v1.api.db.models import ProjectRuntime


class RuntimeAlreadyExists(Exception):
    pass


class RuntimeNotFound(Exception):
    pass


class RuntimeRepository:
    """
    Database-backed runtime repository.
    PostgreSQL is the single source of truth.
    """

    async def create(
        self,
        project_name: str,
        project_root: str,
        image: str,
        container_name: str,
    ) -> ProjectRuntime:
        exists = await ProjectRuntime.filter(
            project_name=project_name
        ).exists()

        if exists:
            raise RuntimeAlreadyExists(
                f"Runtime already exists for project: {project_name}"
            )

        return await ProjectRuntime.create(
            project_name=project_name,
            project_root=project_root,
            container_name=container_name,
            image=image,
            status="stopped",
        )

    async def get(self, project_name: str) -> ProjectRuntime:
        try:
            return await ProjectRuntime.get(project_name=project_name)
        except DoesNotExist:
            raise RuntimeNotFound(
                f"No runtime found for project: {project_name}"
            )

    async def list_all(self) -> List[ProjectRuntime]:
        return await ProjectRuntime.all()

    async def update_status(
        self,
        project_name: str,
        status: str,
    ) -> None:
        updated = await ProjectRuntime.filter(
            project_name=project_name
        ).update(status=status)

        if not updated:
            raise RuntimeNotFound(
                f"No runtime found for project: {project_name}"
            )

    async def update_process_status(
            self,
            project_name: str,
            process_status: str,
    ) -> None:
        updated = await ProjectRuntime.filter(
            project_name=project_name
        ).update(process_status=process_status)

        if not updated:
            raise RuntimeNotFound(
                f"No runtime found for project: {project_name}"
            )

    async def update_container(
        self,
        project_name: str,
        container_name: str,
    ) -> None:
        updated = await ProjectRuntime.filter(
            project_name=project_name
        ).update(container_name=container_name)

        if not updated:
            raise RuntimeNotFound(
                f"No runtime found for project: {project_name}"
            )

    async def update_last_command(
        self,
        project_name: str,
        command: str,
    ) -> None:
        updated = await ProjectRuntime.filter(
            project_name=project_name
        ).update(last_command=command)

        if not updated:
            raise RuntimeNotFound(
                f"No runtime found for project: {project_name}"
            )

    async def delete(self, project_name: str) -> None:
        deleted = await ProjectRuntime.filter(
            project_name=project_name
        ).delete()

        if not deleted:
            raise RuntimeNotFound(
                f"No runtime found for project: {project_name}"
            )
