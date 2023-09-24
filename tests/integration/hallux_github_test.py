#!/bin/env python
# Copyright: Hallux team, 2023

# HALLUX COMMIT TEST : checks that `hallux fix` command indeed capable of fixing all issues in the test-project(s)
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Final

import pytest
from github import Github, PullRequest, Repository

from hallux.auxilary import set_directory
from hallux.main import main
from hallux.targets.github_proposal import GithubProposalTraget

GITHUB_PULLREQUEST_URL = "https://github.com/halluxdev/hallux/pull/26"


@pytest.mark.skipif(
    os.getenv("GITHUB_TOKEN") is None,
    reason="Env variable GITHUB_TOKEN shall be provided in order to run this test",
)
def test_hallux_github(tmp_proj_dir: str | None = None):
    if "GITHUB_TOKEN" not in os.environ.keys():
        SystemError("GITHUB_TOKEN is not provided")

    if tmp_proj_dir is None:
        if not Path("/tmp/hallux").exists():
            Path("/tmp/hallux").mkdir()
        tmp_proj_dir = tempfile.mkdtemp(dir="/tmp/hallux")

    hallux_git_dir = Path(__file__).resolve().parent.parent.parent
    assert hallux_git_dir.joinpath(".git").exists()

    base_url, repo_name, pr_id = GithubProposalTraget.parse_pr_url(
        GITHUB_PULLREQUEST_URL)
    assert base_url == "https://api.github.com"
    assert repo_name == "halluxdev/hallux"
    assert pr_id == 26

    github = Github(os.environ["GITHUB_TOKEN"], base_url=base_url)
    repo: Repository = github.get_repo(repo_name)
    pull_request: PullRequest = repo.get_pull(pr_id)
    assert pull_request.closed_at is None, "Testing Pull-Request shall be still open"
    CORRESPONDING_COMMIT_SHA: Final[str] = pull_request.head.sha

    # Try to clean-up all existing comments
    existing_comments = pull_request.get_comments()
    if existing_comments.totalCount > 0:
        for comment in existing_comments:
            try:
                comment.delete()
            finally:
                pass

    # re-calculate comments_count
    initial_comments_count: Final[int] = pull_request.get_comments().totalCount

    shutil.copytree(str(hallux_git_dir), tmp_proj_dir,
                    ignore_dangling_symlinks=False, dirs_exist_ok=True)
    with set_directory(Path(tmp_proj_dir)):
        try:
            subprocess.check_output(["git", "reset", "--hard"])
            subprocess.check_output(
                ["git", "fetch", "origin", CORRESPONDING_COMMIT_SHA])
            subprocess.check_output(
                ["git", "checkout", CORRESPONDING_COMMIT_SHA])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # Cannot checkout PR commit

        try:
            main(["hallux", "--cache", "--python",
                 "--github", GITHUB_PULLREQUEST_URL, "."])
        except Exception as e:
            pytest.fail(
                e, pytrace=True
            )  # Fail during running `hallux --python --github https://github.com/halluxai/hallux/pull/26 .`

    processed_comments_count: Final[int] = pull_request.get_comments(
    ).totalCount

    assert processed_comments_count > initial_comments_count

    # Try to clean-up new comments in order not to pollute test-PR
    existing_comments = pull_request.get_comments()
    if existing_comments.totalCount > 0:
        for comment in existing_comments:
            try:
                comment.delete()
            finally:
                pass
