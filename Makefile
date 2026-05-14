# Makefile for Alpaca Project - Pedantic Workflow
# Public tasks that anyone can run (not just VS Code users)
#
# NOTE: C++ tools (clang-format, run-clang-tidy, cppcheck) must be in PATH.
#       Python tools (ruff, mypy, pylint) must also be in PATH.
#       Activate your venv before running, or install tools system-wide.

# Detect python: use activated venv if $$VIRTUAL_ENV is set,
# otherwise fall back to venv/ directory or system python.
ifeq ($(OS),Windows_NT)
	PYTHON := $(shell python .tools/find_python.py)
else
	PYTHON := $(shell python3 .tools/find_python.py 2>/dev/null || python .tools/find_python.py)
endif

PY_FILES := $(shell $(PYTHON) .tools/discover_py_files.py)
CPP_FILES := $(shell $(PYTHON) .tools/discover_cpp_files.py)

# Helpers to avoid repeating long commands
RUN_TIMED := $(PYTHON) .tools/run_timed.py
MAKEQUIET := $(MAKE) --no-print-directory

# ==================== C++ TOOLS ====================

.PHONY: cpp-format-check cpp-format-fix cpp-tidy cpp-check cpp-all

# C++ tools (assume they are in PATH)
CLANG_FORMAT := clang-format
CPPCHECK := cppcheck

## Check C++ formatting (clang-format)
cpp-format-check:
	@echo "[1/7] Running clang-format (C++ style check)..."
	@$(RUN_TIMED) "$(CLANG_FORMAT) --dry-run --Werror --style=file:.clang-format $(CPP_FILES)" 'clang-format'
	@echo ""

## Fix C++ formatting (clang-format)
cpp-format-fix:
	@echo "Fixing C++ formatting with clang-format..."
	"$(CLANG_FORMAT)" -i --style=file:.clang-format $(CPP_FILES)
	@echo "Done. C++ files have been reformatted."
	@echo ""

# Stop MINGW from messing with paths
export MSYS_NO_PATHCONV=1

## Run clang-tidy (C++ logic/perf check)
cpp-tidy: build/compile_commands.json
	@echo "[2/7] Running clang-tidy (C++ logic/perf check)..."
	@$(RUN_TIMED) "$(PYTHON) .tools/run_clang_tidy_parallel.py $(CPP_FILES)" 'clang-tidy'
	@echo ""

## Run cppcheck (C++ safety check)
cpp-check:
	@echo "[3/7] Running cppcheck (C++ safety check)..."
	@$(RUN_TIMED) '$(CPPCHECK) --enable=all --inconclusive --error-exitcode=1 --suppress=missingIncludeSystem $(CPP_FILES)' 'cppcheck'
	@echo ""

# ==================== PYTHON TOOLS ====================

.PHONY: py-format-check py-format-fix py-lint py-type py-static py-all

## Check Python formatting (ruff format)
py-format-check:
	@echo "[4/7] Running ruff format (Python style check)..."
	@$(RUN_TIMED) '$(PYTHON) -m ruff format --check --diff $(PY_FILES)' 'ruff format'
	@echo ""

## Fix Python formatting (ruff format)
py-format-fix:
	@echo "Fixing Python formatting with ruff..."
	$(PYTHON) -m ruff format $(PY_FILES)
	@echo "Done. Python files have been reformatted."
	@echo ""

## Run ruff check (Python linting)
py-lint:
	@echo "[5/7] Running ruff check (Python linting)..."
	@$(RUN_TIMED) '$(PYTHON) -m ruff check $(PY_FILES)' 'ruff check'
	@echo ""

## Run mypy (Python type check)
py-type:
	@echo "[6/7] Running mypy (Python type check)..."
	@$(RUN_TIMED) '$(PYTHON) -m mypy $(PY_FILES)' 'mypy'
	@echo ""

## Run pylint (Python static analysis)
py-static:
	@echo "[7/7] Running pylint (Python static analysis)..."
	@$(RUN_TIMED) '$(PYTHON) -m pylint $(PY_FILES)' 'pylint'
	@echo ""

# ==================== COMPOSITE TASKS ====================

.PHONY: pedantic setup clean

## Run full pedantic workflow (C++ + Python)

pedantic:
	@$(MAKEQUIET) cpp-all && $(MAKEQUIET) py-all
	@echo "============================================"
	@echo "        ALL PEDANTIC CHECKS PASSED          "
	@echo "============================================"

## Run all C++ checks

cpp-all:
	@$(RUN_TIMED) '$(MAKEQUIET) cpp-format-check && $(MAKEQUIET) cpp-tidy && $(MAKEQUIET) cpp-check' 'cpp-all'
	@echo "All C++ checks passed!"
	@$(PYTHON) -c "import sys; print('Files checked:'); [print('  ' + path) for path in sys.argv[1:]]" $(CPP_FILES)
	@echo ""

## Run all Python checks

py-all:
	@$(RUN_TIMED) '$(MAKEQUIET) py-format-check && $(MAKEQUIET) py-lint && $(MAKEQUIET) py-type && $(MAKEQUIET) py-static' 'py-all'
	@echo "All Python checks passed!"
	@$(PYTHON) -c "import sys; print('Files checked:'); [print('  ' + path) for path in sys.argv[1:]]" $(PY_FILES)
	@echo ""

# ==================== SETUP ====================

## Install development dependencies
setup:
	@echo "Using Python: $(PYTHON)"
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv venv
	@echo "Installing development dependencies..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "Installing pre-commit hook..."
	$(PYTHON) -m pre_commit install
	@echo "Done. You can now run 'make pedantic'"

# ==================== BUILD ====================

.PHONY: build

## Build the C++ Python extension
build:
	@echo "Building C++ Python extension..."
	cmake --preset 9800X3D-Clang-Ninja
	cmake --build build --config Release
	@echo "Build complete."

# ==================== CLEANUP ====================

## Remove build artifacts and caches (cross-platform)
clean:
	@echo "Cleaning build artifacts and caches..."
	cmake -E rm -rf .mypy_cache .cache .ruff_cache build venv
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
	@echo ""
	@echo "Python Tools:"
	@echo "  make py-format-check   - Check Python formatting (ruff)"
	@echo "  make py-format-fix     - Fix Python formatting (ruff)"
	@echo "  make py-lint           - Run ruff check (linting)"
	@echo "  make py-type           - Run mypy (type checking)"
	@echo "  make py-static         - Run pylint (static analysis)"
	@echo ""
	@echo "Composite:"
	@echo "  make pedantic          - Run full workflow (C++ + Python)"
	@echo "  make cpp-all           - Run all C++ checks"
	@echo "  make py-all            - Run all Python checks"
	@echo ""
	@echo "Build:"
	@echo "  make build             - Build the C++ Python extension"
	@echo ""
	@echo "Utility:"
	@echo "  make clean             - Remove build artifacts and caches"
	@echo ""
	@echo "Setup:"
	@echo "  make setup             - Install dev dependencies"
	@echo "  make help              - Show this help message"
