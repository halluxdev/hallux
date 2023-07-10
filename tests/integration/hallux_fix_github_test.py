#!/bin/env python
# Copyright: Hallux team, 2023

# HALLUX COMMIT TEST : checks that `hallux fix` command indeed capable of fixing all issues in the test-project(s)
from __future__ import annotations

import tempfile
from typing import Final

import pytest
import shutil
import os
from pathlib import Path
import subprocess
from code_processor import set_directory
from targets.github_proposal_traget import GithubProposalTraget
from github import Github, Repository, PullRequest

GITHUB_PULLREQUEST_URL = "https://github.com/halluxai/hallux/pull/26"


@pytest.mark.skipif(
    os.getenv("GITHUB_TOKEN") == None,
    reason="Env variable GITHUB_TOKEN shall be provided in order to run this test",
)
def test_hallux_fix_github_ruff(tmp_proj_dir: str | None = None):
    if "GITHUB_TOKEN" not in os.environ.keys():
        SystemError("GITHUB_TOKEN is not provided")

    if tmp_proj_dir is None:
        if not Path("/tmp/hallux").exists():
            Path("/tmp/hallux").mkdir()
        tmp_proj_dir = tempfile.mkdtemp(dir="/tmp/hallux")

    hallux_git_dir = Path(__file__).resolve().parent.parent.parent
    assert hallux_git_dir.joinpath(".git").exists()

    base_url, repo_name, pr_id = GithubProposalTraget.parse_pr_url(GITHUB_PULLREQUEST_URL)
    assert base_url == "https://api.github.com"
    assert repo_name == "halluxai/hallux"
    assert pr_id == 26

    github = Github(os.environ["GITHUB_TOKEN"], base_url=base_url)
    repo: Repository = github.get_repo(repo_name)
    pull_request: PullRequest = repo.get_pull(pr_id)
    assert pull_request.closed_at is None, "Testing Pull-Request shall be still open"
    CORRESPONDING_COMMIT_SHA: Final[str] = pull_request.head.sha

    initial_comments_count: Final[int] = pull_request.get_comments().totalCount

    shutil.copytree(str(hallux_git_dir), tmp_proj_dir, ignore_dangling_symlinks=False, dirs_exist_ok=True)
    with set_directory(Path(tmp_proj_dir)):
        try:
            subprocess.check_output(["git", "checkout", CORRESPONDING_COMMIT_SHA])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # Cannot checkout pre-defined commit

        try:
            subprocess.check_output(["hallux", "fix", "--ruff", "--github", GITHUB_PULLREQUEST_URL])
        except subprocess.CalledProcessError as e:
            pytest.fail(
                e, pytrace=True
            )  # Fail during running `hallux fix --ruff --github https://github.com/halluxai/hallux/pull/26`

    processed_comments_count: Final[int] = pull_request.get_comments().totalCount

    assert processed_comments_count > initial_comments_count
