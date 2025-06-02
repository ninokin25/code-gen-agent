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

# Windows用: ws2_32ライブラリをリンク
if (WIN32)
    target_link_libraries(brake_app PRIVATE ws2_32) # ここも PRIVATE を明示するとより一貫します
endif()
