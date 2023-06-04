import sys
import pytest
import uuid
from pathlib import Path
from clang.cindex import Index, TranslationUnitLoadError, Cursor, TranslationUnit

sys.path.append(str(Path(__file__).resolve().parent.parent.joinpath("python")))

from ast_parser import parse_cpp_file

@pytest.mark.parametrize("cpp_filename",
                         [
                             pytest.param(str(Path(__file__).resolve().parent.parent.joinpath("samples", "test1.cpp"))),
                             pytest.param(str(Path(__file__).resolve().parent.parent.joinpath("samples", "test2.cpp")))
                         ],)
def test_ast_parser(cpp_filename: str):
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
        reconstructed_ast : Cursor = index.parse(tmp_filename)
    except:
        pytest.fail("Cannot parse reconstructed file")
    #reconstructed_filename = "/tmp/" + str(uuid.uuid4()) + '.reconstructed.ast'
    #reconstructed_ast.save(reconstructed_filename)

    #for token in true_ast.get_tokens():





