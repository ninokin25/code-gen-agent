# body_app用 CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(body_app C)

set(CMAKE_C_STANDARD 99)

add_executable(body_app main.c doorlock_childlock_control.c udp_receiver.c)

target_include_directories(body_app PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# --- OSごとにリンクするライブラリを切り替え ---
if (UNIX)
    message(STATUS "No special libraries needed for Linux/UNIX")
    # Linux用の追加ライブラリがあればここに記述
else()
    message(STATUS "Linking ws2_32 for Windows/MinGW/MSVC")
    target_link_libraries(body_app ws2_32)
endif()
