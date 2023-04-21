from ast_parser import parse_cpp_file

out = parse_cpp_file('/home/sergey/git/hallux/src/hallux.cpp')
print(out)
# connects, id = process_ast(ast.cursor)
# print('----------------------')
# for kindId, kindConns in connects.items():
#     print(f'TokenKind({kindId}):')
#     for usr, conns in kindConns.items():
#         if len(conns) > 1:
#             print(f"{usr}: {conns}")
