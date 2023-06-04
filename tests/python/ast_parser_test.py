#!/usr/bin/env python3
import sys
import pytest
import uuid
from pathlib import Path
from clang.cindex import Index, Token, Cursor, TranslationUnit

sys.path.append(str(Path(__file__).resolve().parent.parent.joinpath("python")))

from ast_parser import parse_cpp_file

@pytest.mark.parametrize("cpp_filename",
                         [
                             pytest.param(str(Path(__file__).resolve().parent.parent.joinpath("samples", "test1.cpp"))),
                             # ToDo: test2.cpp is not fully reconstructable yet! - handling includes is difficult
                             #pytest.param(str(Path(__file__).resolve().parent.parent.joinpath("samples", "test2.cpp")))
                         ],)


def test_hallux_tree_reconstruction(cpp_filename: str):
    '''
    Tests that Hallux Cpp parser is "fully invertable", i.e. we may reconstruct valid cpp code out of it
    :param cpp_filename:
    :return:
    '''

    tree = parse_cpp_file(cpp_filename)
    tmp_filename = "/tmp/" + str(uuid.uuid4()) + '.cpp'
    with open(tmp_filename, mode='wt') as f:
        tree.save(f)

    index = Index.create()
    try:
        true_ast : TranslationUnit = index.parse(cpp_filename)
    except:
        pytest.fail("Cannot parse given file")

    #true_ast_filename = "/tmp/" + str(uuid.uuid4()) + '.true.ast'
    #true_ast.save(true_ast_filename)

    try:
        reconstr_ast : Cursor = index.parse(tmp_filename)
    except:
        pytest.fail("Cannot parse reconstructed file")
    #reconstructed_filename = "/tmp/" + str(uuid.uuid4()) + '.reconstructed.ast'
    #reconstructed_ast.save(reconstructed_filename)

    true_tokens = true_ast.cursor.get_tokens()
    reconstr_tokens = reconstr_ast.cursor.get_tokens()
    token1 : Token = next(true_tokens)
    token2 : Token = next(reconstr_tokens)

    while token1 is not None and token2 is not None :
        # both lists of tokens and pairwise similar
        assert token1.kind == token2.kind
        assert token1.spelling == token2.spelling

        try:
            token1 = next(true_tokens)
            token2 = next(reconstr_tokens)
        except:
            break








