cmake_minimum_required(VERSION 3.16)
project(code_gen_agent_examples C)


add_subdirectory(brake_app)
add_subdirectory(body_app)

# --------------------------------------------------------------------------------------
# debug information
# --------------------------------------------------------------------------------------
# Top directory of source tree (directory with top-level CMakeLists.txt)
message(STATUS "CMAKE_SOURCE_DIR=${CMAKE_SOURCE_DIR}")
# Build directory corresponding to CMAKE_SOURCE_DIR
message(STATUS "CMAKE_BINARY_DIR=${CMAKE_BINARY_DIR}")
# Directory with CMakeLists.txt currently being processed
message(STATUS "CMAKE_CURRENT_SOURCE_DIR=${CMAKE_CURRENT_SOURCE_DIR}")
# Build directory corresponding to CMAKE_CURRENT_BINARY_DIR
message(STATUS "CMAKE_CURRENT_BINARY_DIR=${CMAKE_CURRENT_BINARY_DIR}")
# Top directory of the current project (directory with CMakeLists.txt using the project command)
message(STATUS "PROJECT_SOURCE_DIR=${PROJECT_SOURCE_DIR}")
# Build directory corresponding to PROJECT_SOURCE_DIR
message(STATUS "PROJECT_BINARY_DIR=${PROJECT_BINARY_DIR}")
# CMake Cross Compiling variable
message(STATUS "CMAKE_CROSSCOMPILING=${CMAKE_CROSSCOMPILING}")
message(STATUS "CMAKE_SYSTEM_PROCESSOR=${CMAKE_SYSTEM_PROCESSOR}")
message(STATUS "CMAKE_HOST_SYSTEM_PROCESSOR=${CMAKE_HOST_SYSTEM_PROCESSOR}")
message(STATUS "CMAKE_C_COMPILER=${CMAKE_C_COMPILER}")
message(STATUS "CMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}")
message(STATUS "CMAKE_INSTALL_SYSCONFDIR=${CMAKE_INSTALL_SYSCONFDIR}")
message(STATUS "CMAKE_INSTALL_PREFIX=${CMAKE_INSTALL_PREFIX}")
message(STATUS "CMAKE_HOST_SYSTEM_NAME: ${CMAKE_HOST_SYSTEM_NAME}")
message(STATUS "CMAKE_SYSTEM_NAME: ${CMAKE_SYSTEM_NAME}")
