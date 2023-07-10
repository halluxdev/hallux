#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

import pytest
from pathlib import Path
from file_diff import FileDiff


@pytest.mark.parametrize(
    "issue_line, radius, propose_lines, expected_lines",
    [
        (4, 2, "2\n3\n4\n\n6", "2\n3\n4\n\n6"),  # normal situation line 5 is removed
        (4, 2, "3\n4\n\n6", "2\n3\n4\n\n6"),  # proposed lines shorter than needed, but still OK
        (4, 2, "3\n\n5", "2\n3\n\n5\n6"),  # proposed lines super short, but still enough to match
        (4, 2, "```\n3\n4\n\n6\n```", "2\n3\n4\n\n6"),  # extra ``` stuff
        (4, 2, "```\n3\n4\n\n6\n```\n", "2\n3\n4\n\n6"),  # extra ``` stuff + \n
        (5, 1, "HAL\n4\nB\n6\nHAL", "4\nB\n6"),  # hallucinations around
        (5, 1, "HAL1\nHAL2\n4\nB\n6\nHAL1\nHAL2", "4\nB\n6"),  # more hallucinations around
        (5, 10, "3\nB\n4", "1\n2\n3\nB\n4\n5\n6\n7\n8\n9\n10"),
    ],
)
def test_file_diff_parametrized(
    issue_line: int, radius: int, propose_lines, expected_lines, test_filename="file_diff_test.txt"
):
    test_file = Path(__file__).resolve().parent.joinpath(test_filename)
    filediff = FileDiff(str(test_file), issue_line=issue_line, radius=radius)
    assert len(filediff.all_lines) == 10
    assert len(filediff.issue_lines) > 0
    assert len(filediff.issue_lines) <= len(filediff.all_lines)

    merge_successfull = filediff.propose_lines(propose_lines, try_merging_lines=True)
    assert merge_successfull
    assert filediff.proposed_lines == expected_lines.split("\n")


def test_file_diff(test_filename="file_diff_test.txt"):
    test_file = Path(__file__).resolve().parent.joinpath(test_filename)
    try:
        FileDiff(str(test_file), issue_line=100)
        pytest.fail("FileDiff shall raise an Exception")
    except Exception:
        pass  # Exception intercepted!

    fd0 = FileDiff(str(test_file), issue_line=4, radius=0)
    assert fd0.issue_lines == ["4"]

    fd1 = FileDiff(str(test_file), issue_line=4, radius=1)
    assert fd1.issue_lines == ["3", "4", "5"]

    fd2 = FileDiff(str(test_file), issue_line=4, radius=2)
    assert fd2.issue_lines == ["2", "3", "4", "5", "6"]

    fd3 = FileDiff(str(test_file), issue_line=4, radius=3)
    assert fd3.issue_lines == ["1", "2", "3", "4", "5", "6", "7"]

    # If proposed change is dramatic, merge is unsuccessful
    assert fd1.propose_lines("3\nA\nB\nC") is False
    assert fd1.propose_lines("A\nB\nC\n5") is False

    fd1_c = FileDiff(str(test_file), issue_line=4, radius=1, issue_line_comment=" #")
    assert fd1_c.issue_lines == ["3", "4 #", "5"]
    fd1_c.propose_lines("\n".join(fd1_c.issue_lines))
    assert fd1_c.proposed_lines == ["3", "4", "5"]


def test_cpp_file_diff_with_real_openai_results(test_filename="../test-cpp-project/cpp/test_cpp_project.cpp"):
    test_file = Path(__file__).resolve().parent.joinpath(test_filename)
    fd = FileDiff(str(test_file), issue_line=21, radius=4, issue_line_comment=" // line 21")
    result = fd.propose_lines(
        '```cpp\n#include <iostream>\n\nvoid missingFunction(int arg) {\n    std::cout << "Missing function called with'
        ' argument: " << arg << std::endl;\n}\n\nint main(int argc, char** argv) {\n    missingFunction(argc);\n\n   '
        " return 0; // line 21\n}\n```\nThe issue in the code was a missing semicolon at the end of line 21."
    )
    assert result
    assert fd.proposed_lines == ["  }", "", "  missingFunction(argc);", "", "    return 0;", "}", ""]

    fd2 = FileDiff(str(test_file), issue_line=21, radius=5, issue_line_comment=" // line 21")
    result = fd2.propose_lines(
        '```cpp\n#include <iostream>\n\nvoid print_usage(char* argv[]) {\n  std::cout << "Usage: " << argv[0] << "'
        ' <filename>" << std::endl;\n}\n\nvoid missingFunction(int argc) {\n  std::cout << "Missing function called'
        ' with " << argc << " argument(s)" << std::endl;\n}\n\nint main(int argc, char* argv[]) {\n '
        " print_usage(argv);\n\n  missingFunction(argc);\n\n  return 0;\n}\n```"
    )
    assert result
    print(fd2.proposed_lines)
    assert fd.proposed_lines == ["  }", "", "  missingFunction(argc);", "", "    return 0;", "}", ""]


def test_python_file_diff_with_real_openai_results(
    test_filename="../test-python-project/python/parse_cpp_tree_test.py",
):
    test_file = Path(__file__).resolve().parent.joinpath(test_filename)
    fd = FileDiff(str(test_file), issue_line=39, radius=4)
    assert fd.issue_lines == [
        "",
        "        try:",
        "            token1 = next(tokens1)",
        "            token2 = next(tokens2)",
        "        except:",
        "            break",
        "",
        "",
        "@pytest.mark.parametrize(",
    ]
    fd.propose_lines(
        "```python\ntry:\n    token1 = next(tokens1)\n    token2 = next(tokens2)\nexcept StopIteration:\n   "
        " break\n\n\n@pytest.mark.parametrize(\n```"
    )
    # ToDo: write assert
