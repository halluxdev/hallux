cmake_minimum_required(VERSION 3.4)

project(hallux)
find_package(nlohmann_json 3.7 REQUIRED)

add_subdirectory(CppParser)
include_directories(CppParser/pub)
add_executable(hallux src/hallux.cpp)
target_link_libraries(hallux PRIVATE cppparser gcov nlohmann_json::nlohmann_json)
