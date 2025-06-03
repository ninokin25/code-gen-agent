
cmake_minimum_required(VERSION 3.16)
project(doorlock_control_test CXX)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --------------------------------------------------
# GoogleTest
# --------------------------------------------------
include(CTest)
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/03597a01ee50ed33e9dfd640b249b4be3799d395.zip
  DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
# For Windows: Prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

# -------------------------------
# Unit tests
# -------------------------------
add_executable(test_doorlock_control
    ${CMAKE_SOURCE_DIR}/tests/test_doorlock_control.cpp
    ${CMAKE_SOURCE_DIR}/src/body_app/doorlock_control.c
)

# C++プロジェクトで必要なC言語のコンパイルフラグ
set_source_files_properties(
    ${CMAKE_SOURCE_DIR}/src/body_app/doorlock_control.c
    PROPERTIES COMPILE_FLAGS "-DBUILDING_DLL"
)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  target_compile_options(test_doorlock_control PRIVATE --coverage -O0)
  target_link_libraries(test_doorlock_control PRIVATE --coverage)
endif()

# C/C++連携のための特別設定
if (CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows" AND CMAKE_COMPILER_IS_GNUCXX)
  # リンクフラグを追加
  set_target_properties(test_doorlock_control PROPERTIES LINK_FLAGS "-Wl,--allow-multiple-definition -Wl,--enable-auto-import")
  # MinGW固有のコンパイラフラグ
  target_compile_options(test_doorlock_control PRIVATE -fno-rtti)
endif()

target_link_libraries(test_doorlock_control PRIVATE gtest gtest_main)

# WindowsでCの依存がある場合
if (CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows")
    target_link_libraries(test_doorlock_control PRIVATE ws2_32)
endif()

target_include_directories(
  test_doorlock_control
  PRIVATE
    ${PROJECT_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}/src/body_app
)
target_link_libraries(test_doorlock_control PRIVATE gtest gtest_main)

# WindowsでCの依存がある場合
if (CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows")
    target_link_libraries(test_doorlock_control PRIVATE ws2_32)
endif()

target_include_directories(
  test_doorlock_control
  PRIVATE
    ${PROJECT_SOURCE_DIR}/src
    ${CMAKE_SOURCE_DIR}/src/body_app
)
add_test(NAME test_doorlock_control COMMAND test_doorlock_control)
