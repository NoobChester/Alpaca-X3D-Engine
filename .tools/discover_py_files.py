#!/usr/bin/env python3
"""Discover Python source files in the project, excluding venv and common caches."""

import pathlib

EXCLUDED_DIRS = {
    "venv",
    ".venv",
    "build",
    "dist",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}


def main() -> None:
    """Find all Python files except those in venv and cache directories."""
    files = sorted(
        str(p).replace("\\", "/")
        for p in pathlib.Path(".").glob("**/*.py")
        if not any(part in EXCLUDED_DIRS for part in p.parts)
    )
    print(" ".join(files))


if __name__ == "__main__":
    main()
