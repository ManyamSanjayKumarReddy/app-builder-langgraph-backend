"""
Purpose:
--------
Defines the security policy for executing structured commands
inside project Docker containers.

This policy is used ONLY for:
-----------------------------
- REST-based command execution (future `/exec` endpoints)
- Backend-triggered command execution

This policy is NOT used for:
----------------------------
- WebSocket terminals
- Interactive shells (xterm.js)

Reason:
-------
Terminal access assumes trusted users during local development
and agent experimentation. Enforcing this policy in terminals
would break legitimate workflows (pip install, debugging, etc.).

Responsibilities:
-----------------
- Allowlist safe, high-level commands (python, pip, flask, etc.)
- Block shell escapes, command chaining, and privilege escalation
- Prevent filesystem traversal and destructive operations
"""

import re
from typing import List, Dict


class CommandRejected(Exception):
    """
    Raised when a command or argument violates the security policy.

    This exception should be caught at the API layer and returned
    as a user-friendly error message.
    """
    pass


# -------------------------------------------------------------------
# BLOCKED PATTERNS
# -------------------------------------------------------------------
# These patterns are ALWAYS forbidden, regardless of command allowlist.
#
# They prevent:
# - Shell command chaining
# - Command substitution
# - Privilege escalation
# - Destructive filesystem access
#
# NOTE:
# -----
# This policy assumes commands are executed WITHOUT a shell
# (subprocess list form, not shell=True).
# -------------------------------------------------------------------

BLOCKED_PATTERNS = [
    r";",              # command chaining
    r"&&",
    r"\|\|",
    r"\|",             # pipes
    r"`",              # command substitution
    r"\$\(",
    r"\.\.",           # path traversal
    r"~",              # home directory access
    r"sudo",           # privilege escalation
    r"ssh",
    r"scp",
    r"curl",
    r"wget",
    r"rm\s+-rf",       # destructive delete
    r"chmod",
    r"chown",
    r"kill",
    r"pkill",
    r"mount",
    r"umount",
]

# Precompile regexes once for performance
_BLOCKED_REGEXES = [re.compile(p) for p in BLOCKED_PATTERNS]


# -------------------------------------------------------------------
# ALLOWED COMMANDS
# -------------------------------------------------------------------
# Defines which top-level commands may be executed via REST APIs.
#
# Structure:
# ----------
# - allow_any_args: True → arguments are not restricted
# - allow_any_args: False → arguments must be explicitly allowlisted
#
# IMPORTANT:
# ----------
# This allowlist is intentionally conservative.
# New commands should be added explicitly and reviewed.
# -------------------------------------------------------------------

ALLOWED_COMMANDS: Dict[str, Dict] = {
    "python": {
        "allow_any_args": True,
    },
    "pip": {
        "allowed_args": ["install", "list", "freeze", "-r"],
        "allow_any_args": False,
    },
    "flask": {
        "allow_any_args": True,
    },
    "uvicorn": {
        "allow_any_args": True,
    },
    "streamlit": {
        "allow_any_args": True,
    },
    "pytest": {
        "allow_any_args": True,
    },
}


# -------------------------------------------------------------------
# INTERNAL HELPERS
# -------------------------------------------------------------------

def _check_blocked(value: str):
    """
    Scan a string for blocked patterns.

    This is applied to:
    - Command name
    - Each argument
    - Working directory (cwd)

    Raises:
    -------
    CommandRejected if a blocked pattern is found.
    """
    for regex in _BLOCKED_REGEXES:
        if regex.search(value):
            raise CommandRejected(
                f"Blocked pattern detected: {regex.pattern}"
            )


# -------------------------------------------------------------------
# PUBLIC VALIDATION API
# -------------------------------------------------------------------

def validate_command(command: str, args: List[str], cwd: str | None = None):
    """
    Validate a structured command before execution.

    Parameters:
    -----------
    command : str
        The executable name (e.g. 'python', 'pip', 'flask')
    args : List[str]
        List of command arguments
    cwd : str | None
        Optional working directory (must be relative)

    Validation Rules:
    -----------------
    - Command must be explicitly allowlisted
    - No shell operators or command substitution
    - No absolute paths or path traversal
    - Arguments must comply with command-specific rules

    Returns:
    --------
    True if validation succeeds

    Raises:
    -------
    CommandRejected if validation fails
    """

    # Command must be present
    if not command:
        raise CommandRejected("Command cannot be empty")

    # Command must be allowlisted
    if command not in ALLOWED_COMMANDS:
        raise CommandRejected(f"Command not allowed: {command}")

    # Validate command name
    _check_blocked(command)

    # Validate each argument
    for arg in args:
        _check_blocked(arg)

    # Validate working directory (relative only)
    if cwd:
        _check_blocked(cwd)
        if cwd.startswith("/"):
            raise CommandRejected("Absolute paths are not allowed")

    policy = ALLOWED_COMMANDS[command]

    # Enforce argument allowlist if required
    if not policy.get("allow_any_args"):
        for arg in args:
            if arg not in policy.get("allowed_args", []):
                raise CommandRejected(
                    f"Argument not allowed for '{command}': {arg}"
                )

    return True
