#!/usr/bin/env python3
"""Discover Python source files in the project, excluding venv and common caches."""

import pathlib


def main() -> None:
    """Find all Python files except those in venv and cache directories."""
    files = sorted(str(p).replace("\\", "/") for p in pathlib.Path(".").glob("**/*.py") if "venv" not in p.parts)
    print(" ".join(files))


if __name__ == "__main__":
    main()
