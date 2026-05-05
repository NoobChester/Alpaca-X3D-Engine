# Makefile for Alpaca Project - Pedantic Workflow
# Public tasks that anyone can run (not just VS Code users)
#
# NOTE: C++ tools (clang-format, run-clang-tidy, cppcheck) must be in PATH.
#       Windows: Use Git Bash with LLVM in PATH, or add LLVM to system PATH.

# Detect tools
VENV_DIR := $(CURDIR)/venv
PYTHON := $(VENV_DIR)/Scripts/python.exe
RUFF := $(VENV_DIR)/Scripts/ruff.exe
MYPY := $(VENV_DIR)/Scripts/mypy.exe
PYLINT := $(VENV_DIR)/Scripts/pylint.exe
PY_FILES := $(wildcard *.py)
# Normalizes slashes and handles relative paths
PYTHON_INC  := $(abspath $(shell "$(PYTHON)" -c "import sysconfig; print(sysconfig.get_path('include'))"))
NANOBIND_INC := $(abspath $(shell "$(PYTHON)" -c "import nanobind; print(nanobind.include_dir())"))

# ==================== C++ TOOLS ====================

.PHONY: cpp-format-check cpp-format-fix cpp-tidy cpp-check cpp-all

# C++ tools (assume they are in PATH)
CLANG_FORMAT := clang-format
CPPCHECK := cppcheck

# Locate the run-clang-tidy script and execute it via Python so Windows cmd works.
RUN_CLANG_TIDY := $(shell "$(PYTHON)" -c "import os, pathlib; names=('run-clang-tidy', 'run-clang-tidy.py', 'run-clang-tidy.exe'); print(next(str(pathlib.Path(directory) / name) for directory in os.environ.get('PATH', '').split(os.pathsep) if directory for name in names if (pathlib.Path(directory) / name).is_file()))")

## Check C++ formatting (clang-format)
cpp-format-check:
	@echo "[1/6] Running clang-format (C++ style check)..."
	"$(CLANG_FORMAT)" --dry-run --Werror --style=file:.clang/.clang-format engine.cpp
	@echo "PASS: clang-format"

## Fix C++ formatting (clang-format)
cpp-format-fix:
	@echo "Fixing C++ formatting with clang-format..."
	"$(CLANG_FORMAT)" -i --style=file engine.cpp
	@echo "Done. engine.cpp has been reformatted."

# Stop MINGW from messing with paths
export MSYS_NO_PATHCONV=1

## Run clang-tidy (C++ logic/perf check)
cpp-tidy: build/compile_commands.json
	@echo "[2/6] Running clang-tidy (C++ logic/perf check)..."
	"$(PYTHON)" "$(RUN_CLANG_TIDY)" \
		-j=16 \
		-config-file=.clang/.clang-tidy \
		-warnings-as-errors="*" \
		-p=build \
		-- \
		-std=c++2c \
		-march=znver5 \
		-Iinclude \
		-isystem$(PYTHON_INC) \
		-isystem$(NANOBIND_INC) \
		engine.cpp
	@echo "PASS: clang-tidy"

## Run cppcheck (C++ safety check)
cpp-check:
	@echo "[3/6] Running cppcheck (C++ safety check)..."
	$(CPPCHECK) --enable=all --inconclusive --error-exitcode=1 --suppress=missingIncludeSystem engine.cpp
	@echo "PASS: cppcheck"

# ==================== PYTHON TOOLS ====================

.PHONY: py-format-check py-format-fix py-lint py-type py-static py-all

## Check Python formatting (ruff format)
py-format-check:
	@echo "[4/6] Running ruff format (Python style check)..."
	$(RUFF) format --check --diff $(PY_FILES)
	@echo "PASS: ruff format"

## Fix Python formatting (ruff format)
py-format-fix:
	@echo "Fixing Python formatting with ruff..."
	$(RUFF) format $(PY_FILES)
	@echo "Done. Python files have been reformatted."

## Run ruff check (Python linting)
py-lint:
	@echo "[5/6] Running ruff check (Python linting)..."
	$(RUFF) check $(PY_FILES)
	@echo "PASS: ruff check"

## Run mypy (Python type check)
py-type:
	@echo "[6/6] Running mypy (Python type check)..."
	$(MYPY) $(PY_FILES)
	@echo "PASS: mypy"

## Run pylint (Python static analysis)
py-static:
	@echo "Running pylint (Python static analysis)..."
	$(PYLINT) $(PY_FILES)
	@echo "PASS: pylint"

# ==================== COMPOSITE TASKS ====================

.PHONY: pedantic pedantic-cpp pedantic-py setup clean

## Run full pedantic workflow (C++ + Python)
pedantic: cpp-all py-all
	@echo "============================================"
	@echo "   ALL PEDANTIC CHECKS PASSED"
	@echo "============================================"

## Run all C++ checks
cpp-all: cpp-format-check cpp-tidy cpp-check
	@echo "All C++ checks passed!"

## Run all Python checks
py-all: py-format-check py-lint py-type py-static
	@echo "All Python checks passed!"

# ==================== SETUP ====================

## Install development dependencies
setup:
	@echo "Installing development dependencies..."
	"$(PYTHON)" -m pip install -r requirements.txt
	@echo "Installing pre-commit hook..."
	"$(PYTHON)" -m pre_commit install
	@echo "Done. You can now run 'make pedantic'"

# ==================== CLEANUP ====================

## Remove build artifacts and caches (cross-platform)
clean:
	@echo "Cleaning build artifacts and caches..."
	cmake -E rm -rf .mypy_cache .cache .ruff_cache build
	cmake -E rm -f engine.pyd engine.pyi
	@echo "Done."

# ==================== HELP ====================

.PHONY: help

help:
	@echo "Alpaca Project - Pedantic Workflow"
	@echo "=================================="
	@echo ""
	@echo "C++ Tools:"
	@echo "  make cpp-format-check  - Check C++ formatting (clang-format)"
	@echo "  make cpp-format-fix    - Fix C++ formatting (clang-format)"
	@echo "  make cpp-tidy          - Run clang-tidy (logic/perf)"
	@echo "  make cpp-check         - Run cppcheck (safety)"
	@echo "  make cpp-all           - Run all C++ checks"
	@echo ""
	@echo "Python Tools:"
	@echo "  make py-format-check   - Check Python formatting (ruff)"
	@echo "  make py-format-fix     - Fix Python formatting (ruff)"
	@echo "  make py-lint           - Run ruff check (linting)"
	@echo "  make py-type           - Run mypy (type checking)"
	@echo "  make py-static         - Run pylint (static analysis)"
	@echo "  make py-all            - Run all Python checks"
	@echo ""
	@echo "Composite:"
	@echo "  make pedantic          - Run full workflow (C++ + Python)"
	@echo "  make pedantic-cpp      - Run C++ workflow only"
	@echo "  make pedantic-py       - Run Python workflow only"
	@echo ""
	@echo "Utility:"
	@echo "  make clean             - Remove build artifacts and caches"
	@echo ""
	@echo "Setup:"
	@echo "  make setup             - Install dev dependencies"
	@echo "  make help              - Show this help message"
