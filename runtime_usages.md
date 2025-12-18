command_policy.py
"""
Purpose:
--------
Defines the security policy for executing commands inside project containers.

Responsibilities:
- Allowlist approved commands (python, pip, flask, etc.)
- Block shell escapes, privilege escalation, and filesystem abuse
- Used ONLY for REST-based command execution (/exec, /run)

NOT used for:
- WebSocket terminals (PTY sessions)
"""

docker_manager.py
"""
Purpose:
--------
Manages Docker container lifecycle for each project.

Responsibilities:
- Create containers with resource limits
- Start, stop, and remove containers
- Persist container state to the database
- Acts as the single authority for container state transitions

Does NOT:
- Execute commands inside containers
- Handle terminals or WebSockets
"""

process_manager.py
"""
Purpose:
--------
Manages long-running processes inside containers (servers, agents).

Responsibilities:
- Start exactly ONE long-running process per project
- Capture stdout/stderr streams
- Gracefully terminate processes

Used for:
- flask run
- uvicorn
- streamlit
- background agent loops

NOT used for:
- Interactive terminals
- Short-lived commands
"""

terminal_manager.py
"""
Purpose:
--------
Provides interactive terminal access (PTY) inside running containers.

Responsibilities:
- Create PTY-backed shell sessions using docker exec
- Stream output continuously via a background reader thread
- Accept raw keystrokes from WebSocket clients (xterm.js)
- Maintain exactly ONE terminal session per project

Security model:
- Terminal access assumes trusted UI users
- No command filtering is applied here by design
"""

repository.py
"""
Purpose:
--------
Database abstraction layer for runtime state.

Responsibilities:
- Create, fetch, update, and delete ProjectRuntime records
- Acts as the single source of truth for runtime metadata
- No business logic or Docker interaction

Guarantee:
- All runtime state must be reflected in the database
"""

reconcile.py
"""
Purpose:
--------
Ensures database runtime state matches actual Docker state on app startup.

Responsibilities:
- Detect missing or stopped containers
- Update DB status accordingly
- Never block application startup

Runs:
- Once during FastAPI lifespan startup
"""

runtime_routes.py
"""
Purpose:
--------
HTTP and WebSocket API surface for runtime management.

Responsibilities:
- Start, stop, delete containers
- Expose runtime status for UI polling
- Provide WebSocket-based interactive terminal access

Design goals:
- Idempotent operations
- UI-safe state transitions
- Agent-friendly orchestration
"""
