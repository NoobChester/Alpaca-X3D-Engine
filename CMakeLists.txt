cmake_minimum_required(VERSION 4.2.3)
project(AlpacaEngine LANGUAGES CXX)



# This silences warnings for any flags injected by CMake or Nanobind
# that clang-cl decides not to use.
add_compile_options("/EHsc")

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

nanobind_add_module(engine engine.cpp)

# --- 4. Target & Zen 5 Optimization ---
target_compile_options(engine PRIVATE
    /W4 /WX
    /clang:-Qunused-arguments  # Silence unused flag warnings (Fixes the build crash)

    # --- Architecture Logic ---
    /clang:-std=c++2c
    /clang:-march=znver5
    /clang:-O3

    # --- SIMD / AVX-512 Hot Path ---
    /clang:-mprefer-vector-width=512
    /clang:-mavx512f /clang:-mavx512dq /clang:-mavx512bw /clang:-mavx512vl

    # --- Stack Alignment Enforcement ---
    /clang:-mstack-alignment=64
    /clang:-mstackrealign

    # --- Fast-Math (Safe Subset) ---
    /clang:-fno-math-errno
    /clang:-fno-trapping-math
    /clang:-fassociative-math
    /clang:-fno-signed-zeros
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