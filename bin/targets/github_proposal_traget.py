# Copyright: Hallux team, 2023

from __future__ import annotations
import subprocess
import os
from github import Github, Repository, PullRequest
from file_diff import FileDiff
from targets.filesystem_target import FilesystemTarget


# Saves Issue Fixes as Github proposals
class GithubProposalTraget(FilesystemTarget):
    def __init__(self, github: str):
        FilesystemTarget.__init__(self)

        elems = github.split("/")
        guthub_api_url = "https://api.github.com"  # ToDo: We should parse this out from github URL string
        repo_name = "halluxai/hallux"  # ToDo: We should parse this out from github URL string
        PR_ID = int(elems[len(elems) - 1])

        if "GITHUB_TOKEN" not in os.environ.keys():
            print("GITHUB_TOKEN is not provided properly")
            exit(6)

        self.github = Github(os.environ["GITHUB_TOKEN"], base_url=guthub_api_url)
        self.repo: Repository = self.github.get_repo(repo_name)
        self.pull_request: PullRequest = self.repo.get_pull(PR_ID)

        if self.pull_request.closed_at is not None:  # self.pull_request.is_merged :
            print(f"Pull Request {PR_ID} is either closed or merged already")
            exit(6)
        latest_github_sha: str = self.pull_request.head.sha
        git_log = subprocess.check_output(["git", "log", "--pretty=oneline"]).decode("utf8")
        local_git_sha = git_log.split("\n")[0].split(" ")[0]

        if local_git_sha != latest_github_sha:
            print(
                f"Local git commit `{local_git_sha}` and head from pull-request `{latest_github_sha}` do not coincide!"
            )
            exit(6)

    def apply_diff(self, diff: FileDiff) -> None:
        FilesystemTarget.apply_diff(self, diff)

    def revert_diff(self) -> None:
        FilesystemTarget.revert_diff(self)

    def commit_diff(self) -> bool:
        commit = self.repo.get_commit(self.pull_request.head.sha)
        body = self.existing_diff.description + "\n```suggestion\n"
        for line in self.existing_diff.proposed_lines:
            body = body + line + "\n"
        body = body + "\n```"
        self.pull_request.create_review_comment(
            body=body, commit=commit, path=self.existing_diff.filename, line=self.existing_diff.issue_line
        )
        FilesystemTarget.revert_diff(self)
        return True
