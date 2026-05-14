# Contributing to Alpaca Engine

Thank you for your interest in contributing to the Alpaca Engine project! This guide will help you get started with the development workflow.

## 🚀 Quick Start

1. **Fork & Clone:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Alpaca-X3D-Engine.git
   cd Alpaca-X3D-Engine
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate

   # Install dependencies (including linting tools):
   pip install -r requirements.txt
   # Install pre-commit hooks:
   pre-commit install
   # or if you have make:
   make setup
   ```
   `make setup` installs the venv dependencies and registers the `pre-commit` hook that runs `make pedantic` before commits.

3. **Build the C++ engine:**
   ```bash
   # Option 1: Using make (recommended)
   make build

   # Option 2: Using cmake directly
   cmake --preset 9800X3D-Clang-Ninja
   cmake --build build --config Release
   ```
   *This copies `engine.pyd` and `engine.pyi` into the project root for local testing and editor support.*

4. **Verify tools are working:**
   ```bash
   make pedantic
   ```

## 🎯 Pedantic Workflow (Required)

This project uses a **Pedantic Workflow** to ensure code quality. All checks must pass before merging.

### What Gets Checked

**C++ Tools (project C++ files):**
- `clang-format` — Code style (Microsoft-based, C++26)
- `clang-tidy` — Logic, performance, modern C++ usage
- `cppcheck` — Safety and potential bugs

**Python Tools (project Python files):**
- `ruff format` — Code formatting (Black-compatible)
- `ruff check` — Linting (fast, comprehensive)
- `mypy` — Static type checking (strict mode)
- `pylint` — Deep static analysis

### How to Run Checks

**Option 1: Using Make directly**
```bash
make build             # Build the C++ extension
make pedantic          # Run full workflow (C++ + Python)
make cpp-all           # C++ checks only
make py-all            # Python checks only
make help              # See all available tasks
```

**Option 2: Using pre-commit**
```bash
pre-commit run --all-files  # Run the same pedantic workflow across the repository
pre-commit                  # On staged files only
pre-commit install          # Register the commit hook in .git/hooks
```

**Note:** On Windows, ensure C++ tools are in PATH. See the "Setting up C++ Tools on Windows" section below for setup instructions.

### Fail-Fast Strategy

The workflow stops on the first error. If `ruff format` fails, it won't run `mypy`. This saves time and gives you clear feedback.

Example error output:
```
FAIL: ruff format found style issues
Run: ruff format <project Python files>
```

## 📝 Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and **run the pedantic workflow:**
   ```bash
   make pedantic
   ```

3. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```
   (Run `make pedantic` before committing.)

4. **Push and create a Pull Request**

## 🛠 Tool Configuration

All tool configurations are in **public files** (not in `.vscode/`):

| Tool | Config File | Description |
|------|-------------|-------------|
| clang-format | `.clang-format` | C++ style rules |
| clang-tidy | `.clang-tidy` | C++ static analysis rules |
| ruff, mypy, pylint | `pyproject.toml` | Python tool configs |

To modify rules, edit these files directly. They apply to everyone who clones the repo.

## 🔧 Prerequisites

### C++ Tools
- **clang-format & clang-tidy:** Install via Visual Studio Build Tools (LLVM component)
  - Path: `C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Tools\Llvm\x64\bin\`
- **cppcheck:** Download from https://cppcheck.sourceforge.io/

### Python Tools
Automatically installed via `make setup` or `pip install -r requirements.txt`:
- ruff (formatting + linting)
- mypy (type checking)
- pylint (static analysis)

## 🪟 Setting up C++ Tools on Windows

### Overview
The Makefile requires C++ tools (clang-format, run-clang-tidy, cppcheck) to be available in your PATH. There are three approaches:

### Approach 1: Add LLVM to System PATH (Recommended for Permanent Setup)

1. **Install Visual Studio Build Tools with LLVM component:**
   - Visual Studio Build Tools includes LLVM/Clang in the VC Tools folder
   - Path: `C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Tools\Llvm\x64\bin\`

2. **Add to System PATH:**
   - Open "Environment Variables" (search in Windows Start menu)
   - Edit `Path` under "System variables"
   - Add: `C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Tools\Llvm\x64\bin`
   - Restart terminal/IDE for changes to take effect

3. **Install cppcheck:**
   - Download from: https://cppcheck.sourceforge.io/
   - Extract to a folder (e.g., `C:\Tools\cppcheck`)
   - Add that folder to PATH

4. **Verify setup:**
   ```powershell
   where.exe clang-format
   where.exe run-clang-tidy
   where.exe cppcheck
   ```
   All three commands should return paths.

### Approach 2: Use Git Bash (Easy Alternative)

Git Bash includes MinGW and can access LLVM tools from Visual Studio Build Tools:

1. **Open Git Bash** (right-click → "Git Bash Here")
2. **Run pedantic checks:**
   ```bash
   cd /c/coding/alpaca
   source venv/Scripts/activate
   make pedantic
   ```

### Approach 3: Use PowerShell with Session-Level PATH (Temporary)

For a single session without modifying system PATH:

```powershell
$env:Path += ";C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Tools\Llvm\x64\bin"
# Add cppcheck path if needed
$env:Path += ";C:\Tools\cppcheck"

# Now run make
make pedantic
```

### Troubleshooting Windows Setup

**Issue: "where: command not found"**
- You're in Git Bash or WSL. Use `which` instead of `where.exe`
- Or use Windows PowerShell/cmd instead

**Issue: clang-format still not found after adding to PATH**
- Close and reopen your terminal (PATH changes require a new shell session)
- Try opening a new PowerShell window or use Git Bash

**Issue: run-clang-tidy.exe: command not found**
- The Makefile launches the `run-clang-tidy` script through Python
- Ensure the LLVM bin directory is correctly added to PATH (see above)

## 💡 Tips

1. **Format on Save:** If using VS Code, install the `charliermarsh.ruff` extension for automatic Python formatting.

2. **Skip Hooks (Emergency Only):**
   ```bash
   git commit --no-verify  # Not recommended!
   ```

3. **Run Individual Tools:**
   ```bash
   make cpp-format-check   # Just check C++ formatting
   make py-type           # Just run mypy
   ```

4. **Fix Formatting Automatically:**
   ```bash
   make cpp-format-fix    # Fix C++ formatting
   make py-format-fix      # Fix Python formatting
   ```

## 🐛 Troubleshooting

**Q: `make` command not found (Windows)**
A: Install MinGW or use Git Bash. See the "Setting up C++ Tools on Windows" section above.

**Q: clang-format not found**
A: Ensure C++ tools are in PATH. Follow the Windows setup guide above (add LLVM to System PATH or use Git Bash).

**Q: mypy throws errors about missing imports**
A: Ensure you've activated the virtual environment and run `make setup`.



## 📜 License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License (see `LICENSE` file).

---

**Questions?** Feel free to open an issue or reach out to the maintainers!
