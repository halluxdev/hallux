#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from hallux.targets.github_proposal import GithubProposalTraget


def test_github_proposal_target():
    (base_url, repo_name, PR_ID) = GithubProposalTraget.parse_pr_url(
        "https://github.com/halluxai/hallux/pull/38")
    assert base_url == "https://api.github.com"
    assert repo_name == "halluxai/hallux"
    assert PR_ID == 38
