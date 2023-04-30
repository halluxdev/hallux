#!/usr/bin/env python3
from __future__ import annotations

import copy
from pathlib import Path
from typing import Final, Tuple, Any

from clang.cindex import *

from ast_node import CursorNode, TokenNode, Location
Config.set_library_file(str(Path(__file__).resolve().parent.parent.joinpath("venv", "lib", "python3.8", "site-packages", "clang", "native", "libclang.so")))


def parse_cpp_file(filename) :
    index = Index.create()
    ast = index.parse(filename)
    return process_ast(ast.cursor)

def print_from_cursor(cursor: Cursor):
    line = ""
    prev_token = None
    for tok in cursor.get_tokens():
        if prev_token is None:
            prev_token = tok
        prev_location = prev_token.location
        prev_token_end_col = prev_location.column + len(prev_token.spelling)
        cur_location = tok.location
        if cur_location.line > prev_location.line:
            print(line)
            line = " " * (cur_location.column - 1)
        else:
            if cur_location.column > (prev_token_end_col):
                line += " "
        line += tok.spelling
        prev_token = tok
    if len(line.strip()) > 0:
        print(line)

def print_cpp_file(filename) :
    index = Index.create()
    ast = index.parse(filename)
    print_from_cursor(ast.cursor)
    #conf.lib.


def print_tokens(tokens):
     for tok in tokens:
         print("||", tok.kind, ": ", tok.spelling, " -> ", tok.location)

def isFirstTokenBeforeNext(current_token: Token, child_token: Token) -> bool:
    if current_token.location is None or child_token.location is None :
        return False
    if str(current_token.location.file) == str(child_token.location.file):
         if int(current_token.location.line) < int(child_token.location.line):
             return True
         if current_token.location.line  == child_token.location.line:
            return current_token.location.column < child_token.location.column
    else:
        return False

    return current_token.spelling != child_token.spelling

def print_token(token, label=""):
    print(f"{label}{token.spelling}", end=" ")
    return None

def process_ast(cursor: Cursor, prev_location = None, level: int = 0, order: int = 0, id: int = 0) -> Tuple[CursorNode|None, int, Any, Any]:
    myId : Final[int] = copy.copy(id)
    id += 1

    current_tokens = cursor.get_tokens()
    current_token: Token | None = None
    try:
        current_token = next(current_tokens)
    except StopIteration:
        pass

    if current_token is None:
        return None, id, None, prev_location
    last_good_token = current_token
    print()
    for i in range(level):
         print("  ", end="")

    # print(f"/*{order}: */", end="")
    # print(f"/*{order} {cursor.kind.name} lvl={level} id={id}", end="")
    # usr = cursor.get_usr()
    # if usr is not None and len(str(usr)) > 0:
    #     print(f" usr={usr}", end="")
    # print(f"*/", end="")

    node = CursorNode(level, order, cursor)


    order = 0
    for _, child_cursor in enumerate(cursor.get_children()):
        child_token = None
        try:
            child_token = next(child_cursor.get_tokens())
        except StopIteration:
            pass
        if child_token is not None:
            while isFirstTokenBeforeNext(current_token, child_token):
                prev_location = print_token(current_token)# , label=f"<A{myId}:{child_index}>")
                leaf = TokenNode(level+1, order, current_token)
                node.add_child(leaf)
                order += 1
                last_good_token = current_token
                try:
                    current_token = next(current_tokens)
                except StopIteration:
                    current_token = last_good_token
                    break
                #if current_token is None:
                #    break
                #    #return node, id, current_token, prev_location

        sub_tree, id, prev_token, prev_location = process_ast(child_cursor, prev_location, level+1, order, id)
        order += 1
        node.add_child(sub_tree)

        if prev_token is not None:
            while isFirstTokenBeforeNext(current_token, prev_token):
                 last_good_token = current_token
                 try:
                     current_token = next(current_tokens)
                 except StopIteration:
                     current_token = last_good_token
                     #current_token = None
                     return node, id, current_token, prev_location

    if level == 0:
        if current_token is not None:
            prev_location = print_token(current_token)#, label=f"<C{myId}>")
            leaf = TokenNode(level+1, order, current_token)
            node.add_child(leaf)
            order += 1
            for current_token in current_tokens:
                prev_location = print_token(current_token)#, label=f"<D{myId}>")
                leaf = TokenNode(level+1, order, current_token)
                node.add_child(leaf)
                order += 1


    return node, id, current_token, prev_location






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