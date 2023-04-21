#!/usr/bin/env python3
from __future__ import annotations
from clang.cindex import *
from  ast_node import KnownNode
Config.set_library_file('/home/sergey/git/hallux/venv/lib/python3.8/site-packages/clang/native/libclang.so')

def parse_cpp_file(filename) :
    index = Index.create()
    ast = index.parse(filename)
    return process_ast(ast.cursor)

def print_cpp_file(filename) :
    index = Index.create()
    ast = index.parse(filename)
    print_from_cursor(ast.cursor)

def print_from_cursor(cursor: Cursor):
    code = []
    line = ""
    prev_token = None
    for tok in cursor.get_tokens():
        if prev_token is None:
            prev_token = tok
        prev_location = prev_token.location
        prev_token_end_col = prev_location.column + len(prev_token.spelling)
        cur_location = tok.location
        if cur_location.line > prev_location.line:
            code.append(line)
            line = " " * (cur_location.column - 1)
        else:
            if cur_location.column > (prev_token_end_col):
                line += " "
        line += tok.spelling
        prev_token = tok
    if len(line.strip()) > 0:
        print(line)


# def print_tokens(cursor: Cursor):
#     tok: Token
#     for tok in cursor.get_tokens():
#         print(tok.kind, ": ", tok.spelling, " -> ", tok.location)

def process_ast(tok: Cursor, connects: dict = None, level: int = 0, order: int = 0, id: int = 0):
    print(f"{id}:", end="")
    for i in range(level):
        print("-", end="")

    usr = tok.get_usr()
    print("(", order, "): ",tok.kind.name,": ", tok.spelling, " -> ", usr)
    tree = KnownNode(level=level, order=order, cursor=tok)

    # if usr is not None and len(usr) > 0:
    #     if tok.kind.value not in connects:
    #         connects[tok.kind.value] = {}
    #
    #     if usr not in connects[tok.kind.value]:
    #         connects[tok.kind.value][usr] = []
    #
    #     connects[tok.kind.value][usr].append(id)

    id += 1
    child_tok: Cursor
    for child_index, child_tok in enumerate(tok.get_children()):
        sub_tree, child_connects = process_ast(child_tok, connects, level+1, child_index, id)
        tree.add_child(sub_tree)

    #     print(tok.kind.value, ": ", tok.spelling, " -> ", tok.location)
    return tree, connects

# def process_code_tree(cur: Cursor, connects: dict = {}, level: int = 0, index: int = 0):
#     for i in range(level):
#         print("-", end="")
#     print(index, ":",  cur.kind.value, "(",cur.kind.name,"): ", cur.spelling)
#
#     if cur.kind.value not in connects:
#         connects[cur.kind.value] = {}
#
#     usr = cur.get_usr()
#     if usr is not None:
#         if usr not in connects[cur.kind.value]:
#             connects[cur.kind.value][usr] = []
#         connects[cur.kind.value][usr].append()
#
#
#     child_tok: Cursor
#     for child_index, child_tok in enumerate(cur.get_children()):
#         child_connects = process_code_tree(child_tok, connects, level+1, child_index)
#
#     #     print(tok.kind.value, ": ", tok.spelling, " -> ", tok.location)
#     return connects


# code = code_from_cursor(ast.cursor)
# for line in code:
#     print(line)

# %%
# Build a graph from the AST using NetworkX
# graph = nx.DiGraph()
# for node in ast.get_children():
#     graph.add_node(node.spelling, kind=node.kind.name)
#     for child in node.get_children():
#         graph.add_edge(node.spelling, child.spelling)
#
# # Convert the graph to a TensorFlow tensor
# adj_matrix = nx.to_numpy_matrix(graph, dtype=np.float32)
# adj_tensor = tf.convert_to_tensor(adj_matrix)
#
# # Build the graph neural network model
# model = tf.keras.Sequential([
#     tf.keras.layers.Input(shape=(adj_tensor.shape[0],)),
#     tf.keras.layers.Dense(64, activation="relu"),
#     tf.keras.layers.Dense(32, activation="relu"),
#     tf.keras.layers.Dense(1, activation="sigmoid")
# ])
#
# # Train the model
# model.compile(optimizer="adam", loss="binary_crossentropy")
# model.fit(adj_tensor, y_train, epochs=10)