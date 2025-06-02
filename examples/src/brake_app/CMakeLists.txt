# brake_app用 CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(brake_app C)

set(CMAKE_C_STANDARD 99)

# 実行ファイル: brake_app
# まずターゲットを定義します。ソースファイルは後から target_sources で追加するので、ここでは空にするか、
# 主要なソースファイル（例: main.c）のみを指定することも可能です。
add_executable(brake_app "") # または add_executable(brake_app)

# ソースファイルをターゲット brake_app に PRIVATE スコープで追加します
target_sources(brake_app PRIVATE
    main.c
    speed_generator.c
    udp_sender.c
)

target_include_directories(brake_app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# --- OSごとにリンクするライブラリを切り替え ---
if (CMAKE_HOST_SYSTEM_NAME STREQUAL "Linux")
    message(STATUS "No special libraries needed for Linux/UNIX")
    # Linux用の追加ライブラリがあればここに記述
else(CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows")
    message(STATUS "Linking ws2_32 for Windows/MinGW/MSVC")
    target_link_libraries(brake_app ws2_32)
else()
    message(STATUS "Host System: Unknown or Generic (${CMAKE_SYSTEM_NAME}). Assuming POSIX-like sockets available without special linking.")
    # その他のUnix系や、CMAKE_SYSTEM_NAME が Generic の場合。
    # 通常、POSIX準拠のシステムであれば追加のリンクは不要です。
endif()
