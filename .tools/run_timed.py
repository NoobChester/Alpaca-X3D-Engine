#!/usr/bin/env python3
"""Run a command and display timing."""

import subprocess
import sys
import time


def _normalize_cmd(command: str) -> str:
    """Normalize command for Windows cmd.exe, which doesn't handle / in paths."""
    if sys.platform != "win32":
        return command
    # Replace / with \ so cmd.exe can find executables like venv/Scripts/python.exe
    return command.replace("/", "\\")


def main() -> None:
    """Execute command with timing."""
    if len(sys.argv) < 3:
        raise SystemExit("Usage: run_timed.py <command> <tool_name>")

    command = _normalize_cmd(sys.argv[1])
    tool_name = sys.argv[2]

    start = time.time()
    returncode = subprocess.call(command, shell=True)
    elapsed = int((time.time() - start) * 1000)

    status = "PASS" if returncode == 0 else "FAIL"
    print(f"{status}: {tool_name} [{elapsed} ms]")
    sys.exit(returncode)


if __name__ == "__main__":
    main()
