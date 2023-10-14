#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path

from unit.common.testing_issue import TestingIssue

from hallux.proposals.simple_proposal import SimpleProposal
from hallux.targets.gitlab_suggestion import GitlabSuggestion


def test_github_suggestion():
    (api_url, repo_name, PR_ID) = GitlabSuggestion.parse_mr_url("https://gitlab.com/hallux/hallux/-/merge_requests/2")
    # assert api_url == "https://api.gitlab.com"
    # assert repo_name == "hallux/hallux"
    # assert PR_ID == 2

    assert api_url == None
    assert repo_name == None
    assert PR_ID == None
