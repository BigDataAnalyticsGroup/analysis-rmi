cmake_minimum_required(VERSION 3.2)

project("analysis-rmi"
    LANGUAGES C CXX
    HOMEPAGE_URL https://github.com/BigDataAnalyticsGroup/analysis-rmi
)

# Set output directories
set(EXECUTABLE_OUTPUT_PATH "${PROJECT_BINARY_DIR}/bin")

# Set compilation flags
SET(CMAKE_CXX_STANDARD 17)
SET(CMAKE_COMPILE_FLAGS             "-W -Wall -pedantic -DLEVEL1_DCACHE_LINESIZE=${LEVEL1_DCACHE_LINESIZE} -DPAGESIZE=${PAGESIZE} -march=native -Wno-variadic-macros -Wno-gnu-zero-variadic-macro-arguments -Wno-gnu-label-as-value")
SET(CMAKE_C_FLAGS                   "${CMAKE_C_FLAGS} ${CMAKE_COMPILE_FLAGS}")
SET(CMAKE_CXX_FLAGS                 "-std=c++17 ${CMAKE_CXX_FLAGS} ${CMAKE_COMPILE_FLAGS}")
SET(CMAKE_CXX_FLAGS_DEBUG           "${CMAKE_CXX_FLAGS_DEBUG} -ggdb3 -fno-omit-frame-pointer -fno-optimize-sibling-calls -fsanitize=address,undefined -fsanitize-address-use-after-scope")
SET(CMAKE_CXX_FLAGS_RELEASE         "${CMAKE_CXX_FLAGS_RELEASE} -O2")
SET(CMAKE_CXX_FLAGS_RELWITHDEBINFO  "${CMAKE_CXX_FLAGS_RELWITHDEBINFO} -ggdb3")

# Directories
include_directories(include)

# Executables
add_executable(example example.cpp)
