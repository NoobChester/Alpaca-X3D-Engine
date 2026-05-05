cmake_minimum_required(VERSION 4.2.3)
project(AlpacaEngine LANGUAGES CXX)

# --- 1. Global Compiler Configuration ---
# Use the MSVC-style flag that clang-cl understands globally.
# This silences the '-std=c++26' warnings for nanobind-static.
add_compile_options(/clang:-std=c++2c)

# Standard CMake variables for dependency compatibility
set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_MSVC_PARALLEL_COMPILE OFF)

# --- 2. Python & Virtual Environment ---
set(Python_EXECUTABLE "${CMAKE_SOURCE_DIR}/venv/Scripts/python.exe")
set(Python_FIND_STRATEGY LOCATION)
set(Python_FIND_VIRTUALENV ONLY)

find_package(Python 3.14 REQUIRED COMPONENTS Interpreter Development.Module)
message(STATUS "LOCKED TO PYTHON: ${Python_EXECUTABLE}")

# --- 3. Nanobind Detection ---
execute_process(
    COMMAND "${Python_EXECUTABLE}" -m nanobind --cmake_dir
    OUTPUT_STRIP_TRAILING_WHITESPACE
    OUTPUT_VARIABLE nanobind_DIR
)

find_package(nanobind CONFIG REQUIRED PATHS "${nanobind_DIR}" NO_DEFAULT_PATH)

# nanobind's CMake config may add some default flags that cause warnings with clang-cl.
if (TARGET nanobind-static)
    target_compile_options(nanobind-static INTERFACE /clang:-Qunused-arguments)
    target_compile_options(nanobind-static INTERFACE /clang:-Wno-unused-command-line-argument)
endif()

nanobind_add_module(engine engine.cpp)

# --- 4. Target & Zen 5 Optimization ---
target_compile_options(engine PRIVATE
    # Warning and error flags for clean code
    /W4                 # Level 4 warnings (highest standard)
    /WX                 # Treat warnings as errors (Strict Enforcement)
    /clang:-Wpedantic   # Flag non-standard C++ extensions
    # MSVC-style driver flag for the dialect
    /clang:-std=c++26
    # Direct Clang frontend flags for your 9800X3D
    /clang:-march=znver5
    /clang:-O3
    /clang:-fno-stack-protector
    # Instead of the full -ffast-math, use these:
    /clang:-fno-math-errno       # Speed up math by not setting 'errno'
    /clang:-fno-trapping-math     # Assume no floating point exceptions
    /clang:-fassociative-math     # Allow reassociation (Enables Vectorization!)
    /clang:-fno-signed-zeros      # Treat -0.0 and 0.0 as the same
    # Force the vectorizer to use the 9800X3D's full width
    /clang:-mprefer-vector-width=512
    # Enable AVX-512 for high-performance math
    /clang:-mavx512f
    /clang:-mavx512dq
    /clang:-mavx512bw
    /clang:-mavx512vl
)

target_link_libraries(engine PRIVATE Python::Module)

# --- 5. Generate Python Type Stubs from C++ Source ---
# Automatically generates engine.pyi from engine.cpp for Pylance
add_custom_command(
    OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/engine.pyi"
    COMMAND "${CMAKE_COMMAND}" -E env "PYTHONPATH=$<TARGET_FILE_DIR:engine>"
            "${Python_EXECUTABLE}" -m nanobind.stubgen -m engine -o "${CMAKE_CURRENT_SOURCE_DIR}/engine.pyi"
    DEPENDS engine
    COMMENT "Generating engine.pyi for Pylance type-checking"
)

add_custom_target(generate_stubs ALL DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/engine.pyi")

# --- 6. Synchronization Target ---
# This target is always "out of date" so it always checks the dependency
add_custom_target(copy_engine_pyd ALL
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    $<TARGET_FILE:engine>
    "${CMAKE_CURRENT_SOURCE_DIR}/engine.pyd"
    COMMENT "Syncing engine.pyd to project root for Zen 5 execution"
)

add_dependencies(copy_engine_pyd engine generate_stubs)