#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Final, Tuple, Any
from clang.cindex import *
from ast_node import CursorNode, TokenNode, Location

Config.set_library_file(str(Path(__file__).resolve().parent.parent.joinpath("venv", "lib", "python3.8", "site-packages", "clang", "native", "libclang.so")))

def parse_cpp_file(filename) -> CursorNode:
    index = Index.create()
    ast = index.parse(filename)
    return process_ast(ast.cursor)[0]

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

def inSameFile(current_token: Token, child_token: Token) -> bool:
    if current_token is not None and child_token is not None:
        if current_token.location is not None and child_token.location is not None:
            return str(current_token.location.file) == str(child_token.location.file)
    return False

def isTokenBefore(current_token: Token, child_token: Token) -> bool:
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

def process_ast(cursor: Cursor, level: int = 0, order: int = 0, id: int = 0) -> Tuple[CursorNode|None, int, Token|None]:
    id += 1
    current_tokens = cursor.get_tokens()
    current_token: Token | None = None
    try:
        current_token = next(current_tokens)
    except StopIteration:
        pass

    if current_token is None: # sometimes Cursors end up in the unparsed or missing file
        return None, id, None

    last_child_token = None

    node = CursorNode(level, order, cursor)

    order = 0
    # child Cursors may go interleaved with child Tokens
    # i.e. order of Branches and leafs is arbitrary, so we process them carefully
    for child_cursor in cursor.get_children():
        child_token : Token | None = None
        try: # try to get first token for a child
            child_token = next(child_cursor.get_tokens())
        except StopIteration:
            pass

        # if child_token is in the same file let's iterate current_token until they are equal
        # resulting tokens added as leafs for current node
        if inSameFile(current_token, child_token):
            while isTokenBefore(current_token, child_token):
                leaf = TokenNode(level+1, order, current_token)
                node.add_child(leaf)
                order += 1
                try:
                    current_token = next(current_tokens)
                except StopIteration:
                    break

        sub_tree, id, last_child_token = process_ast(child_cursor, level+1, order, id)
        order += 1
        node.add_child(sub_tree)

        if inSameFile(current_token, last_child_token):
            # iterate current_token to keep up with last_child_token
            while isTokenBefore(current_token, last_child_token):
                 try:
                     current_token = next(current_tokens)
                 except StopIteration:
                     break

    if level == 0:
        if current_token is not None:
            leaf = TokenNode(level+1, order, current_token)
            node.add_child(leaf)
            order += 1
            for current_token in current_tokens:
                leaf = TokenNode(level+1, order, current_token)
                node.add_child(leaf)
                order += 1
    # elif current_token is not None and last_child_token is not None:
    #     if not inSameFile(current_token, last_child_token):
    #         leaf = TokenNode(level+1, order, current_token)
    #         node.add_child(leaf)
    #         order += 1
    #         for current_token in current_tokens:
    #             leaf = TokenNode(level+1, order, current_token)
    #             node.add_child(leaf)
    #             order += 1

    return node, id, current_token
