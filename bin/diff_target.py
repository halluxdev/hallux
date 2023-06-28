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


class DiffTarget(ABC):
    @abstractmethod
    def apply_diff(self, filename: str, start_line: int, end_line: int, new_lines: list[str], message: str) -> None:
        pass

    @abstractmethod
    def revert_diff(self) -> None:
        pass

    @abstractmethod
    def commit_diff(self) -> None:
        pass


class FilesystemTarget(DiffTarget):
    """
    Saves diffs directly into filesystem
    """

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

    def commit_diff(self) -> None:
        self.filename = None
        self.filelines.clear()


class GitCommitTarget(FilesystemTarget):
    """
    Saves diffs into git commits
    """

    def __init__(self):
        FilesystemTarget.__init__(self)
        self.message: str = ""

    def apply_diff(self, filename: str, start_line: int, end_line: int, new_lines: list[str], message: str) -> None:
        FilesystemTarget.apply_diff(self, filename, start_line, end_line, new_lines, message)
        self.message = message

    def revert_diff(self) -> None:
        FilesystemTarget.revert_diff(self)
        self.message = ""

    def commit_diff(self) -> None:
        curr_dir: str = os.getcwd()
        git_dir: str = str(Path(self.filename).parent)
        os.chdir(git_dir)
        subprocess.check_output(["git", "add", os.path.relpath(self.filename, start=git_dir)])
        subprocess.check_output(["git", "commit", "-m", f'"{self.message}"'])
        FilesystemTarget.commit_diff(self)
        os.chdir(curr_dir)


class GithubProposalTraget(DiffTarget):
    def __init__(self, PullRequestID):
        self.PullRequestID = PullRequestID
        pass

    def apply_diff(self, filename: str, start_line: int, end_line: int, new_lines: list[str], message: str) -> None:
        pass

    def revert_diff(self) -> None:
        pass

    def commit_diff(self) -> None:
        pass
