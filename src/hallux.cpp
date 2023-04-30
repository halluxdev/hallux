#include <fstream>
#include <iostream>
#include <cppwriter.h>
#include <cppparser.h>

int main(int argc, char* argv[])
{
  if (argc < 2)
  {
    std::cout << "Usage: " << argv[0] << " filename.cpp" << std::endl;
    return 1;
  }

  CppParser parser;
  auto progUnit = parser.parseFile(argv[1]);
  if (!progUnit)
  {
    std::cout << "Cannot parse: " << argv[1] << std::endl;
    return 2;
  }

  CppWriter writer;
  std::ofstream stm(std::string(argv[1]) + ".reconstructed");
  writer.emit(progUnit.get(), stm);

  return 0;
}