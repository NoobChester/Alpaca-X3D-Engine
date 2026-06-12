#!/usr/bin/env python3
"""Discover C++ source files in the project, excluding venv, build, and cache directories."""

import pathlib


def main() -> None:
    """Find all C++ files except those in venv, build, and cache directories."""
    excludes = {"venv", "build", ".cache"}
    files = sorted(
        str(p).replace("\\", "/")
        for p in pathlib.Path(".").glob("**/*.cpp")
        if not any(excl in p.parts for excl in excludes)
    )
    print(" ".join(files))


if __name__ == "__main__":
    main()
