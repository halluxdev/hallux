from ast_parser import parse_cpp_file, print_cpp_file

#tree = parse_cpp_file('../src/hallux.cpp')
tree = parse_cpp_file('../test/samples/test1.cpp')
tree.print()

