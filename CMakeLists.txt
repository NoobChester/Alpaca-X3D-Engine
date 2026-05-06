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
# Use activated venv if $VIRTUAL_ENV is set, otherwise let CMake find system python.
if(DEFINED ENV{VIRTUAL_ENV})
    if(EXISTS "$ENV{VIRTUAL_ENV}/Scripts/python.exe")
        set(Python_EXECUTABLE "$ENV{VIRTUAL_ENV}/Scripts/python.exe")
    else()
        set(Python_EXECUTABLE "$ENV{VIRTUAL_ENV}/bin/python3")
    endif()
    set(Python_FIND_STRATEGY LOCATION)
    set(Python_FIND_VIRTUALENV ONLY)
else()
    set(Python_FIND_VIRTUALENV FIRST)
endif()

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
    /clang:-Wall
    /clang:-Wextra
    /clang:-Werror
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
set(ENGINE_PYI_OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/engine.pyi")

add_custom_command(
    OUTPUT "${ENGINE_PYI_OUTPUT}"
    COMMAND "${CMAKE_COMMAND}" -E env "PYTHONPATH=$<TARGET_FILE_DIR:engine>"
            "${Python_EXECUTABLE}" -m nanobind.stubgen -m engine -o "${ENGINE_PYI_OUTPUT}"
    DEPENDS engine
    COMMENT "Generating engine.pyi for Pylance type-checking"
)

add_custom_target(generate_stubs ALL DEPENDS "${ENGINE_PYI_OUTPUT}")

# --- 6. Synchronization Target ---
# Copy the generated artifacts into the workspace root for editor and test convenience.
add_custom_target(sync_engine_pyi ALL
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    "${ENGINE_PYI_OUTPUT}"
    "${CMAKE_CURRENT_SOURCE_DIR}/engine.pyi"
    COMMENT "Copying engine.pyi into the workspace root"
)

add_custom_target(sync_engine_pyd ALL
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
    $<TARGET_FILE:engine>
    "${CMAKE_CURRENT_SOURCE_DIR}/engine.pyd"
    COMMENT "Copying engine.pyd into the workspace root"
)

add_dependencies(sync_engine_pyi generate_stubs)
add_dependencies(sync_engine_pyd engine generate_stubs)