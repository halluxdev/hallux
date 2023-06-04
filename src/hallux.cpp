#include <iostream>

int main(int argc, char* argv[])
{
  std::cout << "This is compilable file (part of CMake project) for testing purposes" << std::endl ;
  if (argc < 2)
  {
    std::cout << "Usage: " << argv[0] << " filename.cpp" << std::endl;
    return 1;
  }

  return 0;
}