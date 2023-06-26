#!/usr/bin/env python3

import pytest
import uuid
from pathlib import Path
from clang.cindex import Index, Token, TranslationUnit


from AST.ast_parser import parse_cpp_tree, parse_cpp_list


def assert_cpp_files_similar(cpp_file1: str, cpp_file2: str):
    """
     Checks if 2 cpp files are similar (still might have different formatting)
     Uses LibClang parser
    :param cpp_file1:
    :param cpp_file2:
    :return:
    """
    print(cpp_file1)
    index = Index.create()
    ast1: TranslationUnit = index.parse(cpp_file1)
    ast2: TranslationUnit = index.parse(cpp_file2)
    assert ast1 is not None
    assert ast2 is not None
    tokens1 = ast1.cursor.get_tokens()
    tokens2 = ast2.cursor.get_tokens()
    token1: Token = next(tokens1)
    token2: Token = next(tokens2)

    while token1 is not None and token2 is not None:
        # both lists of tokens and pairwise similar
        assert token1.kind == token2.kind
        assert token1.spelling == token2.spelling

        try:
            token1 = next(tokens1)
            token2 = next(tokens2)
        except:
            break


@pytest.mark.parametrize(
    "cpp_filename",
    [
        pytest.param(str(Path(__file__).resolve().parent.parent.parent.joinpath("samples", "test1.cpp"))),
        # ToDo: test2.cpp is not fully reconstructable yet! - handling includes is difficult
        # pytest.param(str(Path(__file__).resolve().parent.parent.joinpath("samples", "test2.cpp")))
        # pytest.param(str(Path(__file__).resolve().parent.parent.joinpath("samples", "test3_big.cpp"))),
    ],
)
def test_parse_cpp_tree_reconstruction(cpp_filename: str):
    """
    Tests that cpp parser is "fully invertable", i.e. we may reconstruct valid cpp code out of it
    :param cpp_filename:
    :return:
    """

    tree = parse_cpp_tree(cpp_filename)
    tmp_filename = "/tmp/" + str(uuid.uuid4()) + ".cpp"
    with open(tmp_filename, mode="wt") as f:
        tree.save(f)

    assert_cpp_files_similar(cpp_filename, tmp_filename)


@pytest.mark.parametrize(
    "cpp_filename",
    [
        pytest.param(str(Path(__file__).resolve().parent.parent.parent.joinpath("samples", "test1.cpp"))),
        pytest.param(str(Path(__file__).resolve().parent.parent.parent.joinpath("samples", "test2.cpp"))),
        # pytest.param(str(Path(__file__).resolve().parent.parent.parent.joinpath("samples", "test3_big.cpp"))),
    ],
)
def test_parse_cpp_list_reconstruction(cpp_filename: str):
    node_list = parse_cpp_list(cpp_filename)
    tmp_filename = "/tmp/" + str(uuid.uuid4()) + ".cpp"
    with open(tmp_filename, mode="wt") as f:
        for node in node_list:
            node.save2(f)

    assert_cpp_files_similar(cpp_filename, tmp_filename)

