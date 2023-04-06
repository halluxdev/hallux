cmake_minimum_required(VERSION 3.4)

project(hallux)

add_subdirectory(CppParser)
include_directories(CppParser/pub)
add_executable(hallux src/hallux.cpp)
target_link_libraries(hallux PRIVATE cppparser gcov)
