# brake_app用 CMakeLists.txt
cmake_minimum_required(VERSION 3.10)
project(brake_app C)

set(CMAKE_C_STANDARD 99)

# ソースファイル
set(SOURCES
    speed_generator.c
    udp_sender.c
)

# 実行ファイル: brake_app
add_executable(brake_app main.c ${SOURCES})

target_include_directories(brake_app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Windows用: ws2_32ライブラリをリンク
if (WIN32)
    target_link_libraries(brake_app ws2_32)
endif()
