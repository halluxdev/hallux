# Copyright: Hallux team, 2023

from __future__ import annotations
import subprocess
import os
from github import Github, Repository, PullRequest
from file_diff import FileDiff
from targets.filesystem_target import FilesystemTarget


# Saves Issue Fixes as Github proposals
class GithubProposalTraget(FilesystemTarget):
    def __init__(self, config: dict, PullRequestID):
        FilesystemTarget.__init__(self)
        self.config = config
        self.PullRequestID = PullRequestID
        if "GITHUB_TOKEN" not in os.environ.keys():
            print("GITHUB_TOKEN is not provided properly")
            exit(6)

        base_url = self.config["base_url"] if "base_url" in self.config else "https://api.github.com"
        self.github = Github(os.environ["GITHUB_TOKEN"], base_url=base_url)

        if "repo_name_or_id" not in self.config:
            print("repo_name_or_id is not provided properly")
            exit(6)
        repo_name_or_id = self.config["repo_name_or_id"]
        self.repo: Repository = self.github.get_repo(repo_name_or_id)
        self.pull_request: PullRequest = self.repo.get_pull(self.PullRequestID)
        print(self.pull_request.title)

        if self.pull_request.closed_at is not None:  # self.pull_request.is_merged :
            print(f"Pull Request {self.PullRequestID} is either closed or merged already")
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
