import subprocess
from typing import List, Optional, Dict, Tuple

from agent_v1.runtime.command_policy import validate_command
from agent_v1.runtime.repository import RuntimeRepository, RuntimeNotFound


class ExecutionError(Exception):
    pass


class CommandExecutor:
    """
    Executes short-lived commands inside Docker containers.
    Async-safe. PostgreSQL is the source of truth.
    """

    def __init__(self):
        self.repo = RuntimeRepository()

    async def exec(
        self,
        project_name: str,
        command: str,
        args: List[str],
        cwd: Optional[str] = None,
        timeout: int = 60,
        env: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, str, str]:

        # 1. Load runtime from DB
        try:
            runtime = await self.repo.get(project_name)
        except RuntimeNotFound as e:
            raise ExecutionError(str(e))

        if runtime.status != "running":
            raise ExecutionError(
                f"Runtime is not running for project: {project_name}"
            )

        # 2. Validate command
        validate_command(command, args, cwd)

        # 3. Build docker exec command (NO SHELL)
        docker_cmd = ["docker", "exec"]

        if env:
            for k, v in env.items():
                docker_cmd.extend(["-e", f"{k}={v}"])

        workdir = (
            "/workspace"
            if cwd in (None, ".")
            else f"/workspace/{cwd.lstrip('/')}"
        )
        docker_cmd.extend(["-w", workdir])

        docker_cmd.append(runtime.container_name)
        docker_cmd.append(command)
        docker_cmd.extend(args)

        # 4. Execute command
        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            raise ExecutionError("Command execution timed out")
        except Exception as e:
            raise ExecutionError(str(e))

        # 5. Persist last command
        full_command = " ".join([command] + args)
        await self.repo.update_last_command(project_name, full_command)

        return (
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip(),
        )


# Singleton
command_executor = CommandExecutor()
