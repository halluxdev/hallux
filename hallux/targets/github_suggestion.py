# Copyright: Hallux team, 2023

from __future__ import annotations

import copy
import os
import subprocess

from github import Github, GithubObject, PullRequest, Repository

from ..logger import logger
from ..proposals.diff_proposal import DiffProposal
from .filesystem import FilesystemTarget


# Saves Issue Fixes as Github proposals
class GithubSuggestion(FilesystemTarget):
    def __init__(self, pr_url: str | None):
        FilesystemTarget.__init__(self)

        (base_url, repo_name, PR_ID) = GithubSuggestion.parse_pr_url(pr_url)

        if base_url is None:
            logger.warning(f"Cannot parse github PR URL: {pr_url}")
            raise SystemError(f"Cannot parse github PR URL: {pr_url}")

        if "GITHUB_TOKEN" not in os.environ.keys():
            logger.warning("GITHUB_TOKEN is not provided")
            raise SystemError("GITHUB_TOKEN is not provided")

        self.github = Github(os.environ["GITHUB_TOKEN"], base_url=base_url)
        self.repo: Repository = self.github.get_repo(repo_name)
        self.pull_request: PullRequest = self.repo.get_pull(PR_ID)

        if self.pull_request.closed_at is not None:  # self.pull_request.is_merged :
            raise SystemError(f"Pull Request {PR_ID} is either closed or merged already")

        merge_commit_sha: str = self.pull_request.merge_commit_sha
        latest_github_sha: str = self.pull_request.head.sha
        git_log = subprocess.check_output(["git", "log", "--pretty=oneline"]).decode("utf8")
        local_git_sha = git_log.split("\n")[0].split(" ")[0]

        if not (local_git_sha == latest_github_sha or local_git_sha == merge_commit_sha):
            raise SystemError(
                f"Local git commit: `{local_git_sha}` "
                f"do not coinside with the head from pull-request: `{latest_github_sha}` "
                f"nor with the merge commit: `{merge_commit_sha}`"
            )

    @staticmethod
    def parse_pr_url(pr_url: str) -> tuple[str, str, int] | tuple[None, None, None]:
        """
        Tries to parse Pull-Request URL to obtain base_url, repo_name and PR_ID
        :param pr_url: shall look like this: https://BUSINESS.github.com/YOUR_NAME/REPO_NAME/pull/ID
        :return: (base_url, base_url = "https://api." + url_items[0], PR_ID) OR None
        """
        if pr_url.startswith("https://"):
            pr_url = pr_url[len("https://") :]
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

    @staticmethod
    def compact_proposal(proposal: DiffProposal) -> DiffProposal:
        """
        Tries compacting proposed lines by removing overlapping lines of code
        """

        compacted = copy.deepcopy(proposal)

        # try compacting from the beginning
        prop_len = len(compacted.proposed_lines)
        orig_len = len(compacted.issue_lines)
        for i in range(min(prop_len, orig_len)):
            if compacted.proposed_lines[0] == compacted.issue_lines[i]:
                compacted.proposed_lines = compacted.proposed_lines[1:]
                compacted.start_line += 1
            else:
                break

        # now compacting from the end
        prop_len = len(compacted.proposed_lines)
        for i in range(min(prop_len, orig_len)):
            if compacted.proposed_lines[-1] == compacted.issue_lines[-1 - i]:
                compacted.proposed_lines = compacted.proposed_lines[:-1]
                compacted.end_line -= 1
            else:
                break
        return compacted

    def commit_diff(self) -> bool:
        commit = self.repo.get_commit(self.pull_request.head.sha)
        body = self.existing_proposal.description + "\n```suggestion\n"
        compacted = self.compact_proposal(self.existing_proposal)

        for i in range(len(compacted.proposed_lines)):
            line = compacted.proposed_lines[i]
            body += line
            body += "\n" if i < len(compacted.proposed_lines) - 1 else ""
        body = body + "\n```"

        success: bool = True
        try:
            self.pull_request.create_review_comment(
                body=body,
                commit=commit,
                side="RIGHT",
                path=str(compacted.filename),
                line=compacted.end_line,
                start_line=compacted.start_line if compacted.start_line < compacted.end_line else GithubObject.NotSet,
                start_side="RIGHT" if compacted.start_line < compacted.end_line else GithubObject.NotSet,
            )
        except BaseException as ex:
            logger.debug(ex)
            success = False

        # clean local code
        FilesystemTarget.revert_diff(self)
        return success

    def requires_refresh(self) -> bool:
        return False
