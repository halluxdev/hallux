# Copyright: Hallux team, 2023

from __future__ import annotations

import os
import subprocess

from github import Github, GithubException, PullRequest, Repository

from ..proposals.diff_proposal import DiffProposal
from .filesystem import FilesystemTarget


# Saves Issue Fixes as Github proposals
class GithubProposalTraget(FilesystemTarget):
    def __init__(self, pr_url: str):
        FilesystemTarget.__init__(self)

        (base_url, repo_name, PR_ID) = GithubProposalTraget.parse_pr_url(pr_url)

        if base_url is None:
            raise SystemError(f"Cannot parse github PR URL: {pr_url}")

        if "GITHUB_TOKEN" not in os.environ.keys():
            raise SystemError("GITHUB_TOKEN is not provided")

        self.github = Github(os.environ["GITHUB_TOKEN"], base_url=base_url)
        self.repo: Repository = self.github.get_repo(repo_name)
        self.pull_request: PullRequest = self.repo.get_pull(PR_ID)

        if self.pull_request.closed_at is not None:  # self.pull_request.is_merged :
            raise SystemError(
                f"Pull Request {PR_ID} is either closed or merged already")

        latest_github_sha: str = self.pull_request.head.sha
        git_log = subprocess.check_output(
            ["git", "log", "--pretty=oneline"]).decode("utf8")
        local_git_sha = git_log.split("\n")[0].split(" ")[0]

        if local_git_sha != latest_github_sha:
            raise SystemError(
                f"Local git commit `{local_git_sha}` and head from pull-request `{latest_github_sha}` do not coincide!"
            )

    @staticmethod
    def parse_pr_url(pr_url: str) -> tuple[str, str, int] | tuple[None, None, None]:
        """
        Tries to parse Pull-Request URL to obtain base_url, repo_name and PR_ID
        :param pr_url: shall look like this: https://BUSINESS.github.com/YOUR_NAME/REPO_NAME/pull/ID
        :return: (base_url, base_url = "https://api." + url_items[0], PR_ID) OR None
        """
        if pr_url.startswith("https://"):
            pr_url = pr_url[len("https://"):]
            url_items = pr_url.split("/")
            if len(url_items) == 5 and url_items[3] == "pull":
                if url_items[0] == "github.com":
                    base_url = "https://api." + url_items[0]
                else:
                    base_url = "https://api." + url_items[0] + "/api/v3"
                repo_name = url_items[1] + "/" + url_items[2]
                pr_id = int(url_items[4])
                return base_url, repo_name, pr_id
        return None, None, None

    def apply_diff(self, diff: DiffProposal) -> bool:
        for file in self.pull_request.get_files():
            if diff.filename == file.filename:
                FilesystemTarget.apply_diff(self, diff)
                return True
        return False

    def revert_diff(self):
        FilesystemTarget.revert_diff(self)

    def commit_diff(self) -> bool:
        commit = self.repo.get_commit(self.pull_request.head.sha)
        body = self.existing_proposal.description + "\n```suggestion\n"
        for line in self.existing_proposal.proposed_lines:
            body = body + line + "\n"
        body = body + "\n```"

        success: bool = True
        try:
            self.pull_request.create_review_comment(
                body=body,
                commit=commit,
                side="RIGHT",
                path=str(self.existing_proposal.filename),
                line=self.existing_proposal.end_line,
                start_line=self.existing_proposal.start_line,
            )
        except GithubException:
            success = False

        # clean local code
        FilesystemTarget.revert_diff(self)
        return success

    def requires_refresh(self) -> bool:
        return False
