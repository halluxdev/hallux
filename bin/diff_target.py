#!/bin/env python
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


class DiffTarget(ABC):
    @abstractmethod
    def apply_diff(self, filename: str, start_line: int, end_line: int, new_lines: list[str], message: str) -> None:
        pass


class FilesystemTarget(DiffTarget):
    """
    Saves diffs directly into filesystem
    """

    def __init__(self):
        pass

    def apply_diff(self, filename: str, start_line: int, end_line: int, new_lines: list[str], message: str) -> None:
        with open(filename, "rt") as file:
            filelines = file.read().split("\n")

        with open(filename, "wt") as file:
            for line in range(0, start_line + 1):
                file.write(filelines[line] + "\n")

            for code_line in new_lines[1:]:
                file.write(code_line + "\n")

            for line in range(end_line, len(filelines)):
                file.write(filelines[line] + "\n")

            file.close()


class GitCommitTarget(FilesystemTarget):
    """
    Saves diffs into git commits
    """

    def __init__(self):
        FilesystemTarget.__init__(self)

    def apply_diff(self, filename: str, start_line: int, end_line: int, new_lines: list[str], message: str) -> None:
        FilesystemTarget.apply_diff(self, filename, start_line, end_line, new_lines, message)
        subprocess.check_output(["git", "add", filename])
        subprocess.check_output(["git", "commit", "-m", f'"{message}"'])


class GithubProposalTraget(DiffTarget):
    def __init__(self, PullRequestID):
        self.PullRequestID = PullRequestID
        pass
