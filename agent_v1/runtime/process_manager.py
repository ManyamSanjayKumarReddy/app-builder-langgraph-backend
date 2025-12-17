import subprocess
import threading
from typing import Dict, Optional, List
from queue import Queue, Empty


class ProcessAlreadyRunning(Exception):
    pass


class ManagedProcess:
    def __init__(self, popen: subprocess.Popen):
        self.popen = popen
        self.stdout_queue: Queue[str] = Queue()
        self.stderr_queue: Queue[str] = Queue()
        self.alive = True

        threading.Thread(
            target=self._read_stream,
            args=(popen.stdout, self.stdout_queue),
            daemon=True,
        ).start()

        threading.Thread(
            target=self._read_stream,
            args=(popen.stderr, self.stderr_queue),
            daemon=True,
        ).start()

    def _read_stream(self, stream, queue: Queue):
        try:
            for line in iter(stream.readline, ""):
                if not line:
                    break
                queue.put(line)
        finally:
            self.alive = False

    def terminate(self):
        if self.popen.poll() is None:
            self.popen.terminate()
        self.alive = False


class ProcessManager:
    """
    In-memory manager for long-running docker exec processes.
    """

    def __init__(self):
        self._processes: Dict[str, ManagedProcess] = {}

    def start_process(
        self,
        project_name: str,
        container_name: str,
        command: str,
        args: List[str],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        if project_name in self._processes:
            raise ProcessAlreadyRunning(
                f"Process already running for project: {project_name}"
            )

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

        docker_cmd.append(container_name)
        docker_cmd.append(command)
        docker_cmd.extend(args)

        popen = subprocess.Popen(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        self._processes[project_name] = ManagedProcess(popen)

    def get_process(self, project_name: str) -> ManagedProcess:
        return self._processes[project_name]

    def stop_process(self, project_name: str):
        proc = self._processes.pop(project_name, None)
        if proc:
            proc.terminate()

    def has_process(self, project_name: str) -> bool:
        return project_name in self._processes


# Singleton
process_manager = ProcessManager()
