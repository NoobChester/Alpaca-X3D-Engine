#!/usr/bin/env python3
"""Parallel clang-tidy runner for Alpaca project.

Runs clang-tidy on provided C++ source files with 16 worker threads,
automatically resolving system headers (Python include dir, nanobind include dir).
"""

import concurrent.futures
import shutil
import subprocess
import sys
import sysconfig


def find_clang_tidy() -> str:
    """Locate clang-tidy in PATH."""
    clang_tidy = shutil.which("clang-tidy")
    if not clang_tidy:
        raise SystemExit("ERROR: clang-tidy not found in PATH.")
    return clang_tidy


def get_system_includes() -> tuple[str, str]:
    """Get Python and nanobind include directories."""
    python_inc = sysconfig.get_path("include")
    nanobind_inc = __import__("nanobind").include_dir()
    return python_inc, nanobind_inc


def build_clang_tidy_command(clang_tidy: str, python_inc: str, nanobind_inc: str) -> list[str]:
    """Build base clang-tidy command with common arguments."""
    return [
        clang_tidy,
        "-config-file=.clang-tidy",
        "-warnings-as-errors=*",
        "-p=build",
        "--",
        "-std=c++2c",
        "-march=znver5",
        "-Iinclude",
        f"-isystem{python_inc}",
        f"-isystem{nanobind_inc}",
    ]


def run_tidy_on_file(clang_tidy: str, file_path: str, command: list[str]) -> None:
    """Run clang-tidy on a single file."""
    full_command = [clang_tidy, file_path, *command[1:]]
    subprocess.run(full_command, check=True)


def main() -> None:
    """Run clang-tidy in parallel across source files."""
    if len(sys.argv) < 2:
        raise SystemExit("ERROR: No C++ files provided as arguments.")

    files = sys.argv[1:]

    try:
        # Resolve tools and headers
        clang_tidy = find_clang_tidy()
        python_inc, nanobind_inc = get_system_includes()

        # Build command template
        command = build_clang_tidy_command(clang_tidy, python_inc, nanobind_inc)

        # Run clang-tidy in parallel (16 workers)
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(run_tidy_on_file, clang_tidy, file_path, command) for file_path in files]
            concurrent.futures.wait(futures)
            for future in futures:
                future.result()  # Re-raises any exception

    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
