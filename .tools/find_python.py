#!/usr/bin/env python3
"""Find the appropriate Python interpreter: venv or system."""

import os
import pathlib
import sys


def find_python() -> str:
    """
    Detect Python interpreter priority:
    1. VIRTUAL_ENV environment variable (if activated by user)
    2. venv/ directory (if it exists locally)
    3. system python
    """
    is_windows = sys.platform == "win32"

    # Check VIRTUAL_ENV environment variable (user's explicit choice)
    venv_path = os.getenv("VIRTUAL_ENV")
    if venv_path:
        if is_windows:
            python_exe = pathlib.Path(venv_path) / "Scripts" / "python.exe"
        else:
            python_exe = pathlib.Path(venv_path) / "bin" / "python"
        if python_exe.exists():
            return python_exe.resolve().as_posix()

    # Fall back to local venv/ if it exists (user can avoid by not creating it)
    if is_windows:
        venv_python = pathlib.Path("venv") / "Scripts" / "python.exe"
        if venv_python.exists():
            return venv_python.resolve().as_posix()
    else:
        venv_python3 = pathlib.Path("venv") / "bin" / "python3"
        if venv_python3.exists():
            return venv_python3.resolve().as_posix()

        venv_python = pathlib.Path("venv") / "bin" / "python"
        if venv_python.exists():
            return venv_python.resolve().as_posix()

    # Use system python (user's last resort)
    return "python"


if __name__ == "__main__":
    print(find_python())
