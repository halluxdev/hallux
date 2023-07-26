# Copyright: Hallux team, 2023

from __future__ import annotations

from issues.issue import IssueDescriptor
from proposals.simple_proposal import SimpleProposal


class PythonProposal(SimpleProposal):
    def __init__(
        self,
        issue: IssueDescriptor,
        radius_or_range: int | tuple[int, int] = 4,  # radius or tuple with [start_line, end_line]
        issue_line_comment: str | None = None,
    ):
        super().__init__(issue, radius_or_range, issue_line_comment)

        self.min_starting_offset = 50000
        for line in self.issue_lines:
            self.min_starting_offset = min(self.min_starting_offset, len(line) - len(line.lstrip(" ")))

        if self.min_starting_offset > 0:
            for i, line in enumerate(self.issue_lines):
                self.issue_lines[i] = line[self.min_starting_offset :]

            self.proposed_lines = self.issue_lines

    def _merge_lines(self, proposed_lines: list[str]) -> bool:
        if self.min_starting_offset > 0:
            offset = " " * self.min_starting_offset

            for i, line in enumerate(self.proposed_lines):
                proposed_lines[i] = offset + line

        return super()._merge_lines(proposed_lines)
