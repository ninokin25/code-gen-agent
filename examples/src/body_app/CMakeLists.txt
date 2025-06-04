# body_app用 CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(body_app C)
cmake_policy(SET CMP0135 NEW)

set(CMAKE_C_STANDARD 99)

add_executable(body_app
    main.c
    doorlock_control.c
    udp_receiver.c
)

target_include_directories(body_app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# --- OSごとにリンクするライブラリを切り替え ---
if (CMAKE_HOST_SYSTEM_NAME STREQUAL "Linux")
    message(STATUS "No special libraries needed for Linux/UNIX")
    # Linux用の追加ライブラリがあればここに記述
elseif (CMAKE_HOST_SYSTEM_NAME STREQUAL "Windows")
    message(STATUS "Linking ws2_32 for Windows/MinGW/MSVC")
    target_link_libraries(body_app ws2_32)
else()
    message(STATUS "Host System: Unknown or Generic (${CMAKE_SYSTEM_NAME}). Assuming POSIX-like sockets available without special linking.")
    # その他のUnix系や、CMAKE_SYSTEM_NAME が Generic の場合。
    # 通常、POSIX準拠のシステムであれば追加のリンクは不要です。
endif()
