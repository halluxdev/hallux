# Copyright: Hallux team, 2023

from __future__ import annotations
import copy


# Struct to keep all relevant info about found code fix in one place
class FileDiff:
    filename: str
    issue_line: int
    start_line: int
    end_line: int
    original_lines: list[str]
    proposed_lines: list[str]
    filelines: list[str]
    description: str
    issue_line_comment: str | None = None

    def __init__(
        self, filename: str, line: int, radius: int = 4, issue_line_comment: str | None = None, description: str = ""
    ):
        with open(filename, "rt") as file:
            self.filelines = file.read().split("\n")
        self.filename = filename
        self.description = description
        self.issue_line = line
        self.start_line = max(0, line - radius)
        self.end_line = min(len(self.filelines) - 1, line + radius)
        self.original_lines = copy.copy(self.filelines[self.start_line : self.end_line])
        if issue_line_comment is not None:
            self.issue_line_comment = issue_line_comment
            self.original_lines[line - self.start_line] += issue_line_comment

    def propose_lines(self, query_result: str):
        self.proposed_lines = query_result.split("\n")
        for i in range(len(self.proposed_lines)):
            line: str = self.proposed_lines[i]
            if self.issue_line_comment is not None and line.endswith(self.issue_line_comment):
                self.proposed_lines[i] = line[: -len(self.issue_line_comment)]
                break
