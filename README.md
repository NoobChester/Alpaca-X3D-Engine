# Alpaca-X3D-Engine (IN DEVELOPMENT)

A high-performance quantitative trading engine for [Alpaca](https://alpaca.markets/) built with **C++26**, **Python 3.14**, and **nanobind**. Specifically engineered for **AMD Zen 5 (Ryzen 7 9800X3D)**, leveraging 512-bit wide SIMD (AVX-512) for ultra-low latency execution.

## 🧠 Why both C++ and Python?

This engine is architected to solve the "Two-Language Problem" by separating high-level strategy from low-level execution—an industry standard at firms like Jane Street and Optiver.

### 1. Python for Research & Orchestration (The "Brain")
* **Agility:** Python allows for rapid iteration of trading strategies and seamless integration with the **Alpaca API**.
* **Ecosystem:** Leverages **NumPy** and **Pandas** for high-level data manipulation before passing the "hot-path" math to the C++ core.

### 2. C++ for Execution & SIMD (The "Muscle")
* **Hardware Mastery:** Python cannot natively address the **zmm registers** of the **9800X3D**. C++ allows the LLVM compiler to generate **AVX-512** instructions, processing 8 double-precision floats in a single clock cycle.
* **Deterministic Latency:** By bypassing the Python interpreter for signal calculations, we eliminate the performance variability caused by Python’s Global Interpreter Lock (GIL).

### 3. Nanobind: The Zero-Copy Bridge
* **Shared Memory:** Unlike standard wrappers, **nanobind** allows the C++ core to reach directly into the memory address of NumPy arrays. This results in **zero-copy data transfer**, providing the convenience of Python with the sub-millisecond latency of pure C++.

## 🚀 Performance Profile

* **ISA:** Optimized for `znver5` using AVX-512 foundation (`zmm` registers).
* **Math:** Compiled with `-march=znver5` and `/clang:-fassociative-math` to enable auto-vectorization of signal hot-paths.
* **Latency:** Minimal function prologue overhead via `/clang:-fno-stack-protector`.
* **Bindings:** Zero-copy memory mapping between C++ and NumPy using `nanobind`.

## 🛠 Prerequisites

* **CPU:** AMD Ryzen 7 9800X3D (with AVX-512 support).
* **Compiler:** LLVM/Clang 19+ (`clang-cl`).
* **Build System:** CMake + Ninja.
* **Environment:** Python 3.14+.

## 📦 Setup & Build

1. **Clone & Environment:**
   ```powershell
   git clone https://github.com/NoobChester/Alpaca-X3D-Engine.git
   cd Alpaca-X3D-Engine
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
   `make setup` installs the venv dependencies and registers the `pre-commit` hook that runs `make pedantic` before each commit.

2. **Configure (Ninja):**
   ```powershell
   cmake --preset 9800X3D-Clang-Ninja
   ```

3. **Build:**
   ```powershell
   # Option 1: Using make (recommended)
   make build

   # Option 2: Using cmake directly
   cmake --build build --config Release
   ```
   *The build copies `engine.pyd` and `engine.pyi` into the project root for convenience.*

## ⚡ Technical Optimization Guide

### 1. Zero-Copy Python Integration
To maintain the performance edge of the 9800X3D, this engine utilizes **nanobind** for zero-copy data transfer:
* **Memory Mapping:** Uses `nb::ndarray` to map NumPy arrays directly to C++ pointers without duplication.
* **GIL Management:** Heavy mathematical paths utilize `nb::gil_scoped_release` to prevent Python's Global Interpreter Lock from bottlenecking the 512-bit execution threads.

### 2. Critical Implementation Details
When modifying the engine logic, pay attention to these hardware-level constraints:
* **Alignment:** Ensure all data buffers are **64-byte aligned** to prevent "misaligned access" penalties when loading into `zmm` registers.
* **Hot-Path Isolation:** Keep all high-frequency signal loops inside the C++ layer; only return final signals/orders to the Python orchestration layer.

### 3. Memory & Hardware Optimizations
* **std::span** Utilized C++20 views for memory-safe interfacing with NumPy arrays. To ensure maximum compiler throughput, these are unwrapped to `__restrict` raw pointers within the "hot path" to eliminate pointer aliasing concerns during vectorization.
* **std::assume_aligned** Guarantees memory alignment on 64-byte boundaries. This allows the compiler to utilize `VMOVAPD` (Aligned Move) instructions, enabling single-cycle loads into **AVX-512 ZMM registers** and preventing performance-degrading cache-line splits.

## 🔍 Hardware Verification

To confirm the compiler successfully generated AVX-512 code for your 9800X3D, run:

```powershell
# Check for ZMM register usage in the disassembly
llvm-objdump -d engine.pyd | Select-String "zmm"
```

## 🎯 Pedantic Workflow (Code Quality)

To ensure your 9800X3D never runs "sub-optimal" code, this project uses a **Pedantic Workflow** that runs a series of checks before every commit:

### Workflow Pipeline

**C++ Tools:**
1. **clang-format** → Fix code style (Microsoft-based, C++26)
2. **clang-tidy** → Check logic, performance, and modern C++ usage
3. **cppcheck** → Check safety and potential bugs

**Python Tools:**
1. **ruff format** → Format Python code (Black-compatible style)
2. **ruff check** → Lint Python code (fast, comprehensive)
3. **mypy** → Static type checking (strict mode, Python 3.14)
4. **pylint** → Deep static analysis (design, complexity)

**Run checks manually:**
```powershell
# Build the C++ extension
make build

# Run full workflow across the repository
make pedantic

# Run the installed pre-commit hook checks on staged files only
pre-commit run
```

**Before committing:**
Run `make pedantic` to check the current state locally before creating a commit.

```powershell
# To skip local checks (not recommended):
git commit --no-verify
```

### Configuration Files

| Tool | Config File | Description |
|------|-------------|-------------|
| clang-format | `.clang-format` | C++ style (Microsoft-based, 4-space indent) |
| clang-tidy | `.clang-tidy` | C++ static analysis (performance, safety, modern C++) |
| ruff/mypy/pylint | `pyproject.toml` | Python tools configuration (all in one file) |

### Fail-Fast Approach

The workflow uses a **fail-fast** strategy:
- Stops on the first error (no point running mypy if ruff fails)
- Clear error messages tell you which tool found issues and how to fix them

Example error output:
```
PASS: clang-format
PASS: clang-tidy
FAIL: cppcheck
Run: cppcheck <project C++ files>
```

For detailed setup instructions, editor integration, and troubleshooting, see our [Contributing Guide](CONTRIBUTING.md).

## 📜 Usage

```python
import engine
import numpy as np

# Engine utilizes 512-bit vector paths (8x doubles per clock)
prices = np.random.rand(1024).astype(np.float64)
signals = engine.calculate_signal(prices)  # Modifies array in-place

print(f"Modified price: {prices[0]}")

# Apply mean reversion
data = np.random.rand(512).astype(np.float64)
engine.apply_mean_reversion(data, np.mean(data))
print(f"Mean-reverted: {data[0]}")
```

## 🤝 Contributing

Please read our [Contributing Guide](CONTRIBUTING.md) before submitting PRs. All commits must pass the **Pedantic Workflow** (clang-format, clang-tidy, cppcheck, ruff, mypy, pylint).

Quick start for contributors:
```bash
make build             # Build the C++ extension
make pedantic         # Run all checks
```

## ⚖️ License
Apache 2.0
