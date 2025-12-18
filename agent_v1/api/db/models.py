from tortoise import fields
from tortoise.models import Model


class ProjectRuntime(Model):
    """
    Persistent runtime state for each generated project.

    Design Principles:
    ------------------
    - Backend manages ONLY the Docker container lifecycle.
    - Application processes (Flask / FastAPI / Streamlit / agents)
      are user-controlled via WebSocket terminal.
    - No backend-level process tracking is performed.

    This model intentionally avoids process-level state
    to prevent false or misleading runtime information.
    """

    id = fields.UUIDField(pk=True)

    # Unique project identifier (matches generated project folder)
    project_name = fields.CharField(
        max_length=255,
        unique=True,
        index=True,
    )

    # Absolute path to project directory on host
    project_root = fields.TextField()

    # Docker container name bound to this project
    container_name = fields.CharField(
        max_length=255,
        unique=True,
    )

    # Base image used for the container runtime
    image = fields.CharField(
        max_length=255,
        default="python:3.11-slim",
    )

    # Docker container lifecycle state
    # Values: running | stopped
    status = fields.CharField(
        max_length=32,
        default="stopped",
    )

    # Optional audit field for last executed command
    # (purely informational, not a source of truth)
    last_command = fields.TextField(
        null=True,
    )

    # Metadata
    created_at = fields.DatetimeField(
        auto_now_add=True,
    )

    updated_at = fields.DatetimeField(
        auto_now=True,
    )

    class Meta:
        table = "project_runtime"

    def __str__(self):
        return f"<Runtime {self.project_name} ({self.status})>"
