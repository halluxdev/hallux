#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path

import pytest
from unit.common.testing_issue import TestingIssue

from hallux.proposals.simple_proposal import SimpleProposal


@pytest.mark.parametrize(
    "issue_line, radius, propose_lines, expected_lines",
    [
        # normal situation line 5 is removed
        (4, 2, "2\n3\n4\n\n6\n", "2\n3\n4\n\n6\n"),
        # proposed lines shorter than needed, but still OK
        (4, 2, "3\n4\n\n6\n", "2\n3\n4\n\n6\n"),
        # proposed lines super short, but still enough to match
        (4, 2, "3\n\n5\n", "2\n3\n\n5\n6\n"),
        (4, 2, "```\n3\n4\n\n6\n```", "2\n3\n4\n\n6\n"),  # extra ``` stuff
        (4, 2, "```\n3\n4\n\n6\n```\n\n", "2\n3\n4\n\n6\n"),  # extra ``` stuff + \n
        (5, 1, "HAL\n4\nB\n6\nHAL", "4\nB\n6\n"),  # hallucinations around
        (5, 1, "HAL1\nHAL2\n4\nB\n6\nHAL1\nHAL2", "4\nB\n6\n"),  # more hallucinations around
        (5, 10, "3\nB\n4\n", "1\n2\n3\nB\n4\n5\n6\n7\n8\n9\n10"),
    ],
)
def test_simple_proposal_parametrized(
    issue_line: int, radius: int, propose_lines, expected_lines, test_filename="simple_proposal_test.txt"
):
    test_file = str(Path(__file__).resolve().parent.joinpath(test_filename))
    test_issue = TestingIssue(test_file, issue_line=issue_line)

    proposal = SimpleProposal(issue=test_issue, radius_or_range=radius)
    assert len(proposal.all_lines) == 10
    assert len(proposal.issue_lines) > 0
    assert len(proposal.issue_lines) <= len(proposal.all_lines)

    merge_successfull = proposal._merge_lines(proposal._split_lines(propose_lines))
    assert merge_successfull
    assert proposal.proposed_lines == proposal._split_lines(expected_lines)


def test_simple_proposal(test_filename="simple_proposal_test.txt"):
    test_file = str(Path(__file__).resolve().parent.joinpath(test_filename))
    try:
        test_issue = TestingIssue(test_file, issue_line=100)
        SimpleProposal(test_issue)
        pytest.fail("FileDiff shall raise an Exception")
    except Exception:
        pass  # Exception intercepted!

    test_issue2 = TestingIssue(test_file, issue_line=4)
    fd0 = SimpleProposal(test_issue2, radius_or_range=0)
    assert fd0.issue_lines == ["4\n"]

    fd1 = SimpleProposal(test_issue2, radius_or_range=1)
    assert fd1.issue_lines == ["3\n", "4\n", "5\n"]

    fd2 = SimpleProposal(test_issue2, radius_or_range=2)
    assert fd2.issue_lines == ["2\n", "3\n", "4\n", "5\n", "6\n"]

    fd3 = SimpleProposal(test_issue2, radius_or_range=3)
    assert fd3.issue_lines == ["1\n", "2\n", "3\n", "4\n", "5\n", "6\n", "7\n"]

    # If proposed change is dramatic, merge is unsuccessful
    # assert fd1._merge_lines("3\nA\nB\nC".split("\n")) is False
    # assert fd1._merge_lines("A\nB\nC\n5".split("\n")) is False

    # fd1_c = SimpleProposal(test_issue2, radius_or_range=1)
    # assert fd1_c.issue_lines == ["3", "4", "5"]
    # fd1_c._merge_lines(fd1_c.issue_lines)
    # assert fd1_c.proposed_lines == ["3", "4", "5"]


def test_cpp_file_diff_with_real_openai_results(test_filename="../../test-cpp-project/cpp/test_cpp_project.cpp"):
    test_file = Path(__file__).resolve().parent.joinpath(test_filename)
    test_issue = TestingIssue(str(test_file), issue_line=21)
    fd = SimpleProposal(test_issue, radius_or_range=4)
    real_output = fd._split_lines(
        '```cpp\n#include <iostream>\n\nvoid missingFunction(int arg) {\n    std::cout << "Missing function called with'
        ' argument: " << arg << std::endl;\n}\n\nint main(int argc, char** argv) {\n    missingFunction(argc);\n\n   '
        " return 0; // line 21\n}\n```\nThe issue in the code was a missing semicolon at the end of line 21."
    )

    result = fd._merge_lines(real_output)
    assert result
    assert fd.proposed_lines == [
        "  }\n",
        "\n",
        "void missingFunction(int arg) {\n",
        '    std::cout << "Missing function called with argument: " << arg << std::endl;\n',
        "}\n",
        "\n",
        "int main(int argc, char** argv) {\n",
        "    missingFunction(argc);\n",
        "\n",
        "    return 0; // line 21\n",
        "}\n",
    ]

    fd2 = SimpleProposal(test_issue, radius_or_range=5)
    real_output2 = fd._split_lines(
        '```cpp\n#include <iostream>\n\nvoid print_usage(char* argv[]) {\n  std::cout << "Usage: " << argv[0] << "'
        ' <filename>" << std::endl;\n}\n\nvoid missingFunction(int argc) {\n  std::cout << "Missing function called'
        ' with " << argc << " argument(s)" << std::endl;\n}\n\nint main(int argc, char* argv[]) {\n '
        " print_usage(argv);\n\n  missingFunction(argc);\n\n  return 0;\n}\n```"
    )
    result = fd2._merge_lines(real_output2)
    assert result
    print(fd2.proposed_lines)
    assert fd.proposed_lines == [
        "  }\n",
        "\n",
        "void missingFunction(int arg) {\n",
        '    std::cout << "Missing function called with argument: " << arg << std::endl;\n',
        "}\n",
        "\n",
        "int main(int argc, char** argv) {\n",
        "    missingFunction(argc);\n",
        "\n",
        "    return 0; // line 21\n",
        "}\n",
    ]
