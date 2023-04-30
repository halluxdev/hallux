from ast_parser import parse_cpp_file, print_cpp_file

#print_cpp_file('/home/sergey/git/hallux/src/hallux.cpp')

#out, connects,

tree, max_id, _, _ = parse_cpp_file('/home/sergey/git/hallux/src/hallux.cpp')
tree.print()
#print(out)
#out.print()


# connects, id = process_ast(ast.cursor)
# print('----------------------')
# for kindId, kindConns in connects.items():
#     print(f'TokenKind({kindId}):')
#     for usr, conns in kindConns.items():
#         if len(conns) > 1:
#             print(f"{usr}: {conns}")
