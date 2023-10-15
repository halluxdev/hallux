#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

import os
from pathlib import Path

import pytest
import requests

from hallux.proposals.simple_proposal import SimpleProposal
from hallux.targets.gitlab_suggestion import GitlabSuggestion
from tests.unit.common.testing_issue import TestingIssue


def test_github_suggestion():
    (api_url, proj_name, MR_IID) = GitlabSuggestion.parse_mr_url("https://gitlab.com/hallux/hallux/-/merge_requests/2")
    assert api_url == "https://gitlab.com/api/v4"
    assert proj_name == "hallux%2Fhallux"
    assert MR_IID == 2
    assert GitlabSuggestion.parse_mr_url("https://github.com/hallux/hallux/-/merge_requests/2") is None
    assert GitlabSuggestion.parse_mr_url("https://gitlab.com/halluxhallux/-/merge_requests/2") is None
    assert GitlabSuggestion.parse_mr_url("https://gitlab.com/hallux/hallux-/merge_requests/2") is None
    assert GitlabSuggestion.parse_mr_url("https://gitlab.com/hallux/hallux/-merge_requests/2") is None


@pytest.mark.skipif("GITLAB_TOKEN" not in os.environ.keys(), reason="GITLAB_TOKEN is not provided")
def test_gitlab_access():
    gitlab = GitlabSuggestion("https://gitlab.com/hallux/hallux/-/merge_requests/2")
    assert gitlab.mr_iid == 2
    assert gitlab.base_sha == "711e79030a933c60959daaea9850eb07f49e0a8f"
    assert gitlab.start_sha == "711e79030a933c60959daaea9850eb07f49e0a8f"
    assert gitlab.head_sha == "be17ffe7211e232aeaf3f142bf2e647786e551db"
    assert "hallux/targets/github_suggestion.py" in gitlab.changed_files


@pytest.mark.skipif("GITLAB_TOKEN" not in os.environ.keys(), reason="GITLAB_TOKEN is not provided")
def test_gitlab_test_gitlab():
    base_url = "https://gitlab.com/api/v4"
    project_name = "hallux%2Fhallux"
    mr_iid = 2
    data = {}
    data["position[position_type]"] = "text"
    data["position[base_sha]"] = "711e79030a933c60959daaea9850eb07f49e0a8f"
    data["position[head_sha]"] = "be17ffe7211e232aeaf3f142bf2e647786e551db"
    data["position[start_sha]"] = "711e79030a933c60959daaea9850eb07f49e0a8f"
    data["position[old_path]"] = "hallux/targets/github_proposal.py"
    data["position[new_path]"] = "hallux/targets/github_suggestion.py"
    data["position[new_line]"] = "18"
    data["position[old_line]"] = "18"
    data["body"] = "Suka Blya!\n```suggestion:-0+0\nclass GithubSuggestion(FilesystemTarget):\n```"
    request_url: str = f"{base_url}/projects/{project_name}/merge_requests/{mr_iid}/discussions"
    headers = {"PRIVATE-TOKEN": f"{os.environ['GITLAB_TOKEN']}"}  # , "Content-Type": "text"
    mr_response = requests.post(request_url, headers=headers, data=data)
    print(mr_response.status_code)
    print(mr_response.text)
    assert mr_response.status_code == 201
    mr_json = mr_response.json()
    assert mr_json is not None
    assert len(mr_json["id"]) > 10
    assert "individual_note" in mr_json


def test_diff_line_parser():
    diff_lines = " -14,15 +17,18 "
    old_lines, new_lines = GitlabSuggestion.diff_line_parser(diff_lines)
    assert old_lines == [14, 15]
    assert new_lines == [17, 18]


@pytest.mark.skipif("GITLAB_TOKEN" not in os.environ.keys(), reason="GITLAB_TOKEN is not provided")
def test_gitlab_write_suggestion_changed_line():
    gitlab = GitlabSuggestion("https://gitlab.com/hallux/hallux/-/merge_requests/2")
    issue = TestingIssue(
        filename="hallux/targets/github_suggestion.py",
        description="This is description for CHANGED LINE!",
        issue_line=17,
        base_path=Path("/home/sergey/git/hallux"),
    )

    proposal = SimpleProposal(issue, radius_or_range=0)
    proposal.proposed_lines = ["Here is Proposed Change"]
    assert gitlab.write_suggestion(proposal)


@pytest.mark.skipif("GITLAB_TOKEN" not in os.environ.keys(), reason="GITLAB_TOKEN is not provided")
def test_gitlab_write_suggestion_not_changed_line():
    gitlab = GitlabSuggestion("https://gitlab.com/hallux/hallux/-/merge_requests/2")
    issue = TestingIssue(
        filename="hallux/targets/github_suggestion.py",
        description="This is description for NOT CHANGED LINE!",
        issue_line=20,
        base_path=Path("/home/sergey/git/hallux"),
    )

    proposal = SimpleProposal(issue, radius_or_range=0)
    proposal.proposed_lines = ["Another Proposed Change"]
    assert gitlab.write_suggestion(proposal)
