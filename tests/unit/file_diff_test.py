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
    except:
        pass

    fd0 = FileDiff(str(test_file), issue_line=4, radius=0)
    assert fd0.issue_lines == ["4"]

    fd1 = FileDiff(str(test_file), issue_line=4, radius=1)
    assert fd1.issue_lines == ["3", "4", "5"]

    fd2 = FileDiff(str(test_file), issue_line=4, radius=2)
    assert fd2.issue_lines == ["2", "3", "4", "5", "6"]

    fd3 = FileDiff(str(test_file), issue_line=4, radius=3)
    assert fd3.issue_lines == ["1", "2", "3", "4", "5", "6", "7"]

    # If proposed change is dramatic, merge is unsuccessful
    assert fd1.propose_lines("3\nA\nB\nC") == False
    assert fd1.propose_lines("A\nB\nC\n5") == False

    fd1_c = FileDiff(str(test_file), issue_line=4, radius=1, issue_line_comment=" #")
    assert fd1_c.issue_lines == ["3", "4 #", "5"]
    fd1_c.propose_lines("\n".join(fd1_c.issue_lines))
    assert fd1_c.proposed_lines == ["3", "4", "5"]
