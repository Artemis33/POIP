cmake_minimum_required(VERSION 3.16)

project(slotting_project LANGUAGES CXX)

# Standard C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Sources
file(GLOB_RECURSE SRC_FILES
    src/*.cpp
    lib/*.cpp
)

add_executable(slotting ${SRC_FILES})

target_include_directories(slotting PRIVATE
    src
    lib
)

# ----- Gestion par OS -----

if(WIN32)
    message(STATUS "Configuring for Windows")
    target_compile_definitions(slotting PRIVATE OS_WINDOWS)

elseif(APPLE)
    message(STATUS "Configuring for macOS")
    target_compile_definitions(slotting PRIVATE OS_MAC)

elseif(UNIX)
    message(STATUS "Configuring for Linux")
    target_compile_definitions(slotting PRIVATE OS_LINUX)

endif()
