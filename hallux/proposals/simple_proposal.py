# Copyright: Hallux team, 2023 - 2024

from __future__ import annotations

import copy
import difflib
from typing import Final
from pathlib import Path

from hallux.logger import logger

from ..backends.query_backend import QueryBackend
from ..issues.issue import IssueDescriptor
from ..targets.diff import DiffTarget
from .diff_proposal import DiffProposal


# Struct to keep all relevant info about found code fix in one place
class SimpleProposal(DiffProposal):
    def __init__(
        self,
        issue: IssueDescriptor,
        # radius or tuple with [start_line, end_line]
        radius_or_range: int | tuple[int, int] | None = None,
    ):
        """
        :param radius_or_range: "safety buffer" to read around the issue_line
        """
        super().__init__(filename=issue.filename, description=issue.description, issue_line=issue.issue_line)
        self.issue: Final[IssueDescriptor] = issue

        # print full path
        logger.debug(f"Reading: {Path.cwd().joinpath(issue.filename)}")

        with open(issue.filename, "rt") as file:
            self.all_lines: Final[list[str]] = file.read().splitlines(keepends=True)

        if self.issue.issue_line < 1 or self.issue.issue_line > len(self.all_lines):
            raise SystemError(
                f"Wrong issue line {self.issue.issue_line} for file `{issue.filename}`, containing"
                f" {len(self.all_lines)} lines"
            )

        if isinstance(radius_or_range, tuple):
            self._set_code_range(radius_or_range)
        elif radius_or_range is not None:
            self._set_code_radius(radius_or_range)

    def _set_code_range(self, range: tuple[int, int]):
        self.start_line = max(1, range[0])
        self.end_line = min(len(self.all_lines), range[1])
        self.safety_radius = min(self.issue.issue_line - self.start_line, self.end_line - self.issue.issue_line)
        self._set_issue_lines()

    def _set_code_radius(self, radius: int):
        self.safety_radius = abs(int(radius))
        self.start_line = max(1, self.issue.issue_line - self.safety_radius)
        self.end_line = min(len(self.all_lines), self.issue.issue_line + self.safety_radius)
        self._set_issue_lines()

    def _set_issue_lines(self):
        self.issue_lines: list[str] = copy.deepcopy(self.all_lines[self.start_line - 1 : self.end_line])
        self.proposed_lines: list[str] = copy.deepcopy(self.issue_lines)
        if self.issue.line_comment is not None:
            # now because self.issue_lines contain \n or \r\n at the end of each line,
            # adding line comment gets a little bit more involved
            issue_line = self.issue_lines[self.issue.issue_line - self.start_line]
            issue_line = issue_line.split("\n")
            issue_line[0] += self.issue.line_comment
            issue_line = "\n".join(issue_line)
            self.issue_lines[self.issue.issue_line - self.start_line] = issue_line

    def try_fixing(self, query_backend: QueryBackend, diff_target: DiffTarget) -> bool:
        """
        try to find match between original issue_lines and proposed_lines
        1. We know that real change which needs to be done is in the middle of issue_lines
        2. GPT might hallucinate some starting and/or ending codes, but usually keeps provided code too
        3. We need to clear off hallucinated starting- and ending- codes, that's why we have "safety radius" around
        :return True if merge was successful
        """

        user_message_template = (
            query_backend.prompt.get("user")
            if query_backend.prompt.get("user") is not None
            else query_backend.backend.prompt.get("user")
        )

        issue_data = {
            "ISSUE_LANGUAGE": self.issue.language,
            "ISSUE_TYPE": self.issue.issue_type,
            "ISSUE_DESCRIPTION": self.issue.description,
            "ISSUE_FILEPATH": self.issue.filename,
            "ISSUE_LINES": "".join(self.issue_lines),
        }

        user_message = user_message_template.format(**issue_data)
        query_results: list[str] = query_backend.query(user_message, self.issue, issue_lines=self.issue_lines)
        if len(query_results) == 0:
            return False

        proposed_lines: list[str] = query_results[0].splitlines(keepends=True)
        merge_result = self._merge_lines(proposed_lines)

        if merge_result and self.proposed_lines != self.issue_lines:
            return diff_target.apply_diff(self)

        return False

    def _split_lines(self, code: str) -> list[str]:
        return code.splitlines(keepends=True)

    def _merge_lines(self, proposed_lines: list[str]) -> bool:
        if proposed_lines[0].startswith("```"):
            proposed_lines = proposed_lines[1:-1]  # remove first and last line
            if proposed_lines[-1].startswith("```"):
                # if new last line is still ``` (this happens if there was "\n" after ```)
                # remove last line once again
                proposed_lines = proposed_lines[:-1]

        # remove issue.line_comment if it was added
        issue_line_found: int | None = None
        if self.issue.line_comment:
            # Remove from proposed_lines
            for i, line in enumerate(proposed_lines):
                if line.endswith(self.issue.line_comment):
                    proposed_lines[i] = line[: -len(self.issue.line_comment)]
                    issue_line_found = i
                    break

            # Remove from issue_lines
            issue_line_idx = self.issue.issue_line - self.start_line
            if self.issue_lines[issue_line_idx].endswith(self.issue.line_comment):
                self.issue_lines[issue_line_idx] = self.issue_lines[issue_line_idx][: -len(self.issue.line_comment)]

        merge_result: bool
        if issue_line_found is not None:
            # when issue line comment remained in the proposed code
            merge_result = self._merge_from_issue_line(proposed_lines, issue_line_found)
        else:
            # when issue line comment deleted/missing in the proposed code
            merge_result = self._merge_from_both_ends(proposed_lines)

        return merge_result

    def _merge_from_both_ends(self, proposed_lines: list[str]) -> bool:
        # merge starting code
        line_diff: list[str] = list(difflib.ndiff(self.issue_lines, proposed_lines))
        issue_lines_index: int = 0
        prop_lines_index: int = 0

        for i in range(len(line_diff)):  # loop until we find matching line
            if line_diff[i].startswith("+ "):
                prop_lines_index += 1
            elif line_diff[i].startswith("- "):
                issue_lines_index += 1
            elif line_diff[i].startswith("  "):
                proposed_lines = self.issue_lines[:issue_lines_index] + proposed_lines[prop_lines_index:]
                break
            else:
                prop_lines_index += 1
                issue_lines_index += 1

        # safety_radius is a parameter to a Proposal, telling how many lines before and after the issue line to take
        # if issue_lines_index > self.safety_radius - we are outside of safety radius, so the code we want to fix
        if issue_lines_index > self.safety_radius:
            # unsuccessful merge
            logger.debug("Unable to merge from the top")
            self.print_diff(self.issue_lines, proposed_lines)
            return False

        # merge ending code
        # line_diff = list(difflib.ndiff(self.issue_lines, proposed_lines))
        # even though these indexes are positive, they intend to measure offsets from bottom to up
        issue_lines_index = 0
        prop_lines_index = 0

        for i in range(len(line_diff)):  # loop until we find matching line
            if line_diff[-i - 1].startswith("+ "):
                prop_lines_index += 1
            elif line_diff[-i - 1].startswith("- "):
                issue_lines_index += 1
            elif line_diff[-i - 1].startswith("  "):
                proposed_lines = proposed_lines[: -prop_lines_index - 1] + self.issue_lines[-issue_lines_index - 1 :]
                break
            else:
                prop_lines_index += 1
                issue_lines_index += 1

        if issue_lines_index > self.safety_radius:
            # unsuccessful merge
            logger.debug("Unable to merge from the bottom")
            self.print_diff(self.issue_lines, proposed_lines)
            return False

        self.proposed_lines = proposed_lines
        self.print_diff(self.issue_lines, proposed_lines)
        return True

    def _merge_from_issue_line(self, proposed_lines: list[str], found_issue_line_index: int) -> bool:
        """
        If we can find original issue_line within the proposed_lines,
        we may use it for better merge between issue_lines and proposed_lines
        :param proposed_lines:
        :param found_issue_line_index:
        :return:
        """

        def find_first_match(list1: list[str], list2: list[str]) -> tuple[int, int]:
            index1: int = 0
            index2: int = 0
            line_diff: list[str] = list(difflib.ndiff(list1, list2))
            for i in range(len(line_diff)):  # loop until we find matching line
                if line_diff[i].startswith("+ "):
                    index2 += 1
                elif line_diff[i].startswith("- "):
                    index1 += 1
                elif line_diff[i].startswith("  "):
                    return index1, index2
                else:
                    index1 += 1
                    index2 += 1
            return index1, index2

        orig_issue_line_index: Final[int] = self.issue.issue_line - self.start_line
        issue_lines_start = self.issue_lines[:orig_issue_line_index]
        proposed_lines_start = proposed_lines[:found_issue_line_index]
        issue_lines_start.reverse()
        proposed_lines_start.reverse()

        issue_lines_end = self.issue_lines[orig_issue_line_index:]
        proposed_lines_end = proposed_lines[found_issue_line_index:]

        issue_index_above, proposed_index_above = find_first_match(issue_lines_start, proposed_lines_start)
        issue_index_below, proposed_index_below = find_first_match(issue_lines_end, proposed_lines_end)

        self.proposed_lines = (
            self.issue_lines[: orig_issue_line_index - issue_index_above]
            + proposed_lines[
                found_issue_line_index - proposed_index_above : found_issue_line_index + proposed_index_below
            ]
            + self.issue_lines[orig_issue_line_index + issue_index_below :]
        )

        return True
