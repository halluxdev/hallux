# Copyright: Hallux team, 2023

from __future__ import annotations
import copy


# Struct to keep all relevant info about found code fix in one place
from typing import Final


class FileDiff:
    def __init__(
        self,
        filename: str,
        issue_line: int,
        radius: int = 4,
        issue_line_comment: str | None = None,
        description: str = "",
    ):
        with open(filename, "rt") as file:
            self.all_lines: Final[list[str]] = file.read().split("\n")
        self.filename: Final[str] = filename
        self.description: Final[str] = description
        self.issue_line: Final[int] = issue_line
        self.start_line: Final[int] = max(0, issue_line - radius)
        self.end_line: Final[int] = min(len(self.all_lines), issue_line + radius)
        self.issue_lines: Final[list[str]] = copy.copy(self.all_lines[self.start_line - 1 : self.end_line])
        self.proposed_lines: list[str] = []
        self.issue_line_comment = issue_line_comment
        if issue_line_comment is not None:
            self.issue_lines[issue_line - self.start_line] += issue_line_comment

    def propose_lines(self, query_result: str):
        self.proposed_lines = query_result.split("\n")
        for i in range(len(self.proposed_lines)):
            line: str = self.proposed_lines[i]
            if self.issue_line_comment is not None and line.endswith(self.issue_line_comment):
                self.proposed_lines[i] = line[: -len(self.issue_line_comment)]
                break
