# Copyright: Hallux team, 2023

# We have several options where (and how) to send found fixes.
# 1. Most primitive one - it simply to re-write local files
# 2. Little more complicated - rewrite local files, but also make git commit on every change
# 3. Submit all changes onto Github Web Interface as proposals/suggestions
#    This last one requires some extra configuring to be done
# All those approaches are hidden after DiffTarget interface


from __future__ import annotations
from abc import ABC, abstractmethod
import subprocess
import os
from pathlib import Path
from github import Github, Repository, PullRequest


class DiffTarget(ABC):
    @abstractmethod
    def apply_diff(self, filename: str, start_line: int, end_line: int, new_lines: list[str], message: str) -> None:
        pass

    @abstractmethod
    def revert_diff(self) -> None:
        pass

    @abstractmethod
    def commit_diff(self) -> bool:
        """
        :return: true if issues are solved independently
                (i.e. need to increment issue_index in the IssueSolver)
        """
        pass


# Saves diffs directly into local filesystem
class FilesystemTarget(DiffTarget):
    def __init__(self):
        self.filename: str | None = None
        self.filelines: list[str] = []

    def apply_diff(self, filename: str, start_line: int, end_line: int, new_lines: list[str], message: str) -> None:
        if self.filename is not None:
            raise Exception("FilesystemTarget: Cannot apply new diff, before last one committed or reverted")

        self.filename = filename
        with open(self.filename, "rt") as file:
            self.filelines = file.read().split("\n")

        with open(filename, "wt") as file:
            for line in range(0, start_line + 1):
                file.write(self.filelines[line] + "\n")

            for code_line in new_lines[1:]:
                file.write(code_line + "\n")

            for line in range(end_line, len(self.filelines)):
                file.write(self.filelines[line] + "\n")

            file.close()

    def revert_diff(self) -> None:
        if self.filename is not None:
            with open(self.filename, "wt") as file:
                for line in self.filelines:
                    file.write(line + "\n")
            self.filename = None
            self.filelines = []

    def commit_diff(self) -> bool:
        self.filename = None
        self.filelines.clear()
        return False


# Saves fixes into local git commits
class GitCommitTarget(FilesystemTarget):
    def __init__(self):
        FilesystemTarget.__init__(self)
        self.message: str = ""

    def apply_diff(self, filename: str, start_line: int, end_line: int, new_lines: list[str], message: str) -> None:
        FilesystemTarget.apply_diff(self, filename, start_line, end_line, new_lines, message)
        self.message = message

    def revert_diff(self) -> None:
        FilesystemTarget.revert_diff(self)
        self.message = ""

    def commit_diff(self) -> int:
        curr_dir: str = os.getcwd()
        git_dir: str = str(Path(self.filename).parent)
        os.chdir(git_dir)
        subprocess.check_output(["git", "add", os.path.relpath(self.filename, start=git_dir)])
        subprocess.check_output(["git", "commit", "-m", f'"{self.message}"'])
        FilesystemTarget.commit_diff(self)
        os.chdir(curr_dir)
        return 0


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

        self.filename = None
        self.start_line = None
        self.end_line = None
        self.new_lines = []
        self.message = ""

    def apply_diff(self, filename: str, start_line: int, end_line: int, new_lines: list[str], message: str) -> None:
        FilesystemTarget.apply_diff(self, filename, start_line, end_line, new_lines, message)
        self.filename = filename
        self.start_line = start_line
        self.end_line = end_line
        self.new_lines = new_lines
        self.message = message

    def revert_diff(self) -> None:
        FilesystemTarget.revert_diff(self)
        self.filename = None
        self.start_line = None
        self.end_line = None
        self.new_lines = []
        self.message = ""

    def commit_diff(self) -> bool:
        commit = self.repo.get_commit(self.pull_request.head.sha)
        body = self.message + "\n```suggestion\n"
        for line in self.new_lines:
            body + body + line + "\n"
        body = body + "\n```"
        self.pull_request.create_review_comment(body=body, commit=commit, path=self.filename, line=self.start_line + 4)
        FilesystemTarget.revert_diff(self)
        return True
