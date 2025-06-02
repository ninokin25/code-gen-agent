set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
set(CMAKE_C_COMPILER clang)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -c -ansi -nostdinc -fno-common -funsigned-char -fbracket-depth=1000 -std=gnu99 -pedantic")
