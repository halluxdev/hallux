# Copyright: Hallux team, 2023

from __future__ import annotations
import copy
import difflib
from typing import Final


# Struct to keep all relevant info about found code fix in one place
class FileDiff:
    def __init__(
        self,
        filename: str,
        issue_line: int,
        radius: int = 4,
        issue_line_comment: str | None = None,
        description: str = "",
    ):
        """
        :param filename:
        :param issue_line: line where issue is found (numbering starts from 1)
        :param radius: "safety buffer" to read around the issue_line
        :param issue_line_comment: add comment into one line from issue_lines,
        :param description: for storing issue description
        """
        with open(filename, "rt") as file:
            self.all_lines: Final[list[str]] = file.read().split("\n")
        self.filename: Final[str] = str(filename)
        self.description: Final[str] = str(description)
        self.issue_line: Final[int] = abs(int(issue_line))
        self.safety_radius: Final[int] = abs(int(radius))
        if self.issue_line < 1 or self.issue_line > len(self.all_lines):
            raise SystemError(
                f"Wrong issue line {issue_line} for file `{filename}`, containing {len(self.all_lines)} lines"
            )
        self.start_line: Final[int] = max(1, issue_line - radius)
        self.end_line: Final[int] = min(len(self.all_lines), issue_line + radius)
        self.issue_lines: Final[list[str]] = copy.copy(self.all_lines[self.start_line - 1 : self.end_line])
        self.proposed_lines: list[str] = []
        self.issue_line_comment = issue_line_comment
        if issue_line_comment is not None:
            self.issue_lines[issue_line - self.start_line] += issue_line_comment

    def propose_lines(self, query_result: str, try_merging_lines: bool = True) -> bool:
        """
        try to find match between original issue_lines and proposed_lines
        1. We know that real change which needs to be done is in the middle of issue_lines
        2. GPT might hallucinate some starting and/or ending codes, but usually keeps provided code too
        3. We need to clear off hallucinated starting- and ending- codes, that's why we have "safety radius" around
        :return True if merge was successfull
        """
        self.proposed_lines = self.issue_lines  # copy original lines for now, replace with proper lines later
        proposed_lines: list[str] = query_result.split("\n")
        if proposed_lines[0].startswith("```"):
            proposed_lines = proposed_lines[1:-1]  # remove first and last line
            # if new last line is still ``` (this happens if there used to be \n after ```)
            if proposed_lines[-1].startswith("```"):  # remove last line once again
                proposed_lines = proposed_lines[:-1]

        # remove issue_line_comment if it was added
        if self.issue_line_comment is not None:
            for i in range(len(proposed_lines)):
                line: str = proposed_lines[i]
                if line.endswith(self.issue_line_comment):
                    proposed_lines[i] = line[: -len(self.issue_line_comment)]
                    break

        if try_merging_lines:
            # merge starting code
            line_diff: list[str] = list(difflib.ndiff(self.issue_lines, proposed_lines))
            issue_index: int = 0
            prop_index: int = 0

            for i in range(len(line_diff)):  # loop until we find matching line
                if line_diff[i].startswith("+ "):
                    prop_index += 1
                elif line_diff[i].startswith("- "):
                    issue_index += 1
                elif line_diff[i].startswith("  "):
                    proposed_lines = self.issue_lines[:issue_index] + proposed_lines[prop_index:]
                    break
                else:
                    prop_index += 1
                    issue_index += 1

            if issue_index > self.safety_radius:
                # unsuccessful merge
                return False

            # merge ending code
            line_diff: list[str] = list(difflib.ndiff(self.issue_lines, proposed_lines))
            issue_index = 0
            prop_index = 0

            for i in range(len(line_diff)):  # loop until we find matching line
                if line_diff[-i - 1].startswith("+ "):
                    prop_index += 1
                elif line_diff[-i - 1].startswith("- "):
                    issue_index += 1
                elif line_diff[-i - 1].startswith("  "):
                    proposed_lines = proposed_lines[: -prop_index - 1] + self.issue_lines[-issue_index - 1 :]
                    break
                else:
                    prop_index += 1
                    issue_index += 1

            if issue_index > self.safety_radius:
                # unsuccessful merge
                return False

        self.proposed_lines = proposed_lines
        return True
