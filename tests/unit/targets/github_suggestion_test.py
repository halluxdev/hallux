#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path

from unit.common.testing_issue import TestingIssue

from hallux.proposals.simple_proposal import SimpleProposal
from hallux.targets.github_suggestion import GithubSuggestion


def test_github_suggestion():
    (base_url, repo_name, PR_ID) = GithubSuggestion.parse_pr_url("https://github.com/halluxai/hallux/pull/38")
    assert base_url == "https://api.github.com"
    assert repo_name == "halluxai/hallux"
    assert PR_ID == 38


def test_compact_proposal():
    filename = Path(__file__).resolve().parent.parent.joinpath("proposals", "simple_proposal_test.txt")
    issue = TestingIssue(
        filename=str(filename),
        issue_line=5,
    )
    proposal = SimpleProposal(issue, radius_or_range=2)
    assert proposal.issue_lines == ["3\n", "4\n", "5\n", "6\n", "7\n"]
    assert proposal.start_line == 3
    assert proposal.end_line == 7

    proposed_lines = ["3\n", "4AAA\n", "5AAA\n", "NEW LINE\n", "6\n", "7\n"]
    proposal._merge_lines(proposed_lines)
    assert proposal.proposed_lines == proposed_lines

    compacted = GithubSuggestion.compact_proposal(proposal)
    assert compacted.proposed_lines == ["4AAA\n", "5AAA\n", "NEW LINE\n"]
    assert compacted.start_line == 4
    assert compacted.end_line == 5
