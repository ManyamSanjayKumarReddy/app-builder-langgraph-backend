"""
Purpose:
--------
Provides interactive PTY-based terminal access to running containers.

Designed for:
- WebSocket streaming
- xterm.js frontend

Guarantees:
- One terminal session per project
- Continuous, low-latency streaming
"""

import os
import pty
import select
import subprocess
import threading
from queue import Queue


class TerminalSession:
    def __init__(self, container_name: str, workdir: str):
        self.container_name = container_name
        self.workdir = workdir
        self.master_fd = None
        self.process = None
        self.queue = Queue()
        self.alive = True

        self._start_shell()
        self._start_reader()

    def _start_shell(self):
        self.master_fd, slave_fd = pty.openpty()

        self.process = subprocess.Popen(
            [
                "docker", "exec", "-it",
                "-w", self.workdir,
                self.container_name,
                "/bin/bash",
            ],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
        )

        os.close(slave_fd)

    def _start_reader(self):
        def reader():
            while self.alive:
                r, _, _ = select.select([self.master_fd], [], [], 0.1)
                if self.master_fd in r:
                    try:
                        data = os.read(self.master_fd, 4096)
                        if data:
                            self.queue.put(data.decode(errors="ignore"))
                    except OSError:
                        break

        threading.Thread(target=reader, daemon=True).start()

    def write(self, data: str):
        if self.alive:
            os.write(self.master_fd, data.encode())

    def read(self):
        try:
            return self.queue.get_nowait()
        except Exception:
            return None

    def close(self):
        self.alive = False
        try:
            self.process.terminate()
        except Exception:
            pass


class TerminalManager:
    def __init__(self):
        self.sessions = {}

    def get_or_create(self, project_name: str, container_name: str):
        if project_name not in self.sessions:
            self.sessions[project_name] = TerminalSession(
                container_name=container_name,
                workdir="/workspace",
            )
        return self.sessions[project_name]

    def close(self, project_name: str):
        session = self.sessions.pop(project_name, None)
        if session:
            session.close()


terminal_manager = TerminalManager()
