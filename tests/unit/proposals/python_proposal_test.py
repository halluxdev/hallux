#!/bin/env python
# Copyright: Hallux team, 2023 - 2024

from __future__ import annotations

from inspect import currentframe, getframeinfo
from pathlib import Path

from unit.common.testing_issue import TestingIssue

from hallux.proposals.python_proposal import PythonProposal


def test_python_proposal():
    line = getframeinfo(currentframe()).lineno
    print("A")
    print("B")
    print("C")

    issue = TestingIssue(
        filename=str(Path(__file__).resolve()),
        language="python",
        issue_line=line + 2,
        line_comment="  # This is THE line",
    )
    proposal = PythonProposal(issue, radius_or_range=1)
    assert proposal.code_offset == 4
    assert proposal.issue_lines == ['print("A")', 'print("B")  # This is THE line', 'print("C")']

    assert proposal._merge_lines(['print("A")', 'print("BBBBBB")', 'print("C")']) is True

    proposal2 = PythonProposal(issue, extract_function=True)
    assert line > proposal2.start_line >= line - 2
    line_end = getframeinfo(currentframe()).lineno
    assert line_end + 2 >= proposal2.end_line >= line_end


def test_python_proposal_code_offset():
    line = getframeinfo(currentframe()).lineno
    if line > 0:
        issue = TestingIssue(filename=str(Path(__file__).resolve()), language="python", issue_line=line + 3)
        # This line is used for testing
        proposal0 = PythonProposal(issue, radius_or_range=0)
        assert proposal0.code_offset == 8

        proposal1 = PythonProposal(issue, radius_or_range=1)
        assert proposal1.code_offset == 8
        proposal2 = PythonProposal(issue, radius_or_range=2)
        assert proposal2.code_offset == 4
        proposal4 = PythonProposal(issue, radius_or_range=4)
        assert proposal4.code_offset == 0


def test_python_file_diff_with_real_openai_results(
    test_filename="../../test-python-project/python/parse_cpp_tree_test.py",
):
    test_file = Path(__file__).resolve().parent.joinpath(test_filename)
    test_issue = TestingIssue(str(test_file), issue_line=39)
    fd = PythonProposal(test_issue, radius_or_range=3)
    assert fd.issue_lines == [
        "try:",
        "    token1 = next(tokens1)",
        "    token2 = next(tokens2)",
        "except: # <-- fix around this line 39",
        "    break",
        "",
        "",
    ]

    merge_result = fd._merge_lines(
        [
            "```python",
            "try:",
            "    token1 = next(tokens1)",
            "    token2 = next(tokens2)",
            "except StopIteration:",
            "    break",
            "```",
        ]
    )

    assert merge_result == True
