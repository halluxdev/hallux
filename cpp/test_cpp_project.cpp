#include <iostream>

void missingFunction(int& argc);

void print_usage(char* argv[])
{
  std::cout << "Usage: " << argv[0] << " filename.cpp" << std::endl;
  return 1;
}

int main(int argc, char* argv[])
{
  std::cout << "This is compilable file (part of CMake project) for testing purposes" << std::endl ;
  if (argc < 2)
  {
    print_usage();
  }

  missingFunction(argc);

  return 0
}


