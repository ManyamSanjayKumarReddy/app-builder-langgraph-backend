import re
from typing import List, Dict


class CommandRejected(Exception):
    """Raised when a command violates security policy."""


# BLOCKED PATTERNS (GLOBAL)
# NOTE:
# - `/` is intentionally blocked to prevent *any* path usage from user input.
# - Absolute and relative paths are resolved internally by the executor.
BLOCKED_PATTERNS = [
    r";",              # command chaining
    r"&&",
    r"\|\|",           # logical OR
    r"\|",             # pipe
    r"`",              # command substitution
    r"\$\(",
    r"\.\.",           # path traversal
    r"~",              # home directory
    r"/",              # ANY path usage (intentional)
    r"sudo",
    r"ssh",
    r"scp",
    r"curl",
    r"wget",
    r"rm\s+-rf",
    r"chmod",
    r"chown",
    r"kill",
    r"pkill",
    r"mount",
    r"umount",
]

# Precompile regexes once
_BLOCKED_REGEXES = [re.compile(p) for p in BLOCKED_PATTERNS]


# ALLOWED COMMANDS
ALLOWED_COMMANDS: Dict[str, Dict] = {
    "python": {
        "allowed_args": ["-m"],
        "allow_any_args": True,
    },
    "pip": {
        "allowed_args": ["install", "list", "freeze", "-r"],
        "allow_any_args": False,
    },
    "npm": {
        "allowed_args": ["install", "run"],
        "allow_any_args": True,
    },
    "npx": {
        "allowed_args": [],
        "allow_any_args": True,
    },
    "node": {
        "allowed_args": [],
        "allow_any_args": True,
    },
    "uvicorn": {
        "allowed_args": [],
        "allow_any_args": True,
    },
    "pytest": {
        "allowed_args": [],
        "allow_any_args": True,
    },
}


def _check_blocked_patterns(value: str):
    for regex in _BLOCKED_REGEXES:
        if regex.search(value):
            raise CommandRejected(
                f"Blocked pattern detected: `{regex.pattern}`"
            )


def validate_command(command: str, args: List[str], cwd: str | None = None):
    """
    Validates a structured command before execution.

    Rules:
    - Only allow predefined commands
    - No shell operators
    - No path traversal or filesystem access
    - Arguments are allowlisted per command
    """

    if not command:
        raise CommandRejected("Command cannot be empty")

    if command not in ALLOWED_COMMANDS:
        raise CommandRejected(f"Command not allowed: {command}")

    # Validate command itself
    _check_blocked_patterns(command)

    # Validate arguments
    for arg in args:
        _check_blocked_patterns(arg)

    # Validate cwd (relative only, no paths)
    if cwd:
        _check_blocked_patterns(cwd)
        if cwd.startswith("/"):
            raise CommandRejected("Absolute paths are not allowed")

    # Argument allowlist enforcement
    policy = ALLOWED_COMMANDS[command]

    if not policy["allow_any_args"]:
        i = 0
        while i < len(args):
            arg = args[i]

            # Allowed flags
            if arg in policy["allowed_args"]:
                # Special case: -r <file>
                if arg == "-r":
                    if i + 1 >= len(args):
                        raise CommandRejected("'-r' requires a requirements file")

                    req_file = args[i + 1]
                    _check_blocked_patterns(req_file)

                    # Do NOT allow path traversal or absolute paths
                    if req_file.startswith("/") or ".." in req_file:
                        raise CommandRejected("Invalid requirements file path")

                    i += 2
                    continue

                i += 1
                continue

            raise CommandRejected(
                f"Argument not allowed for `{command}`: {arg}"
            )

    return True
