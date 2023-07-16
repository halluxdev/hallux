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
        radius_or_range: int | tuple[int, int] = 4,  # radius or tuple with [start_line, end_line]
        issue_line_comment: str | None = None,
        description: str = "",
    ):
        """
        :param filename:
        :param issue_line: line where issue is found (numbering starts from 1)
        :param radius_or_range: "safety buffer" to read around the issue_line
        :param issue_line_comment: add comment into one line from issue_lines,
        :param description: for storing issue description
        """
        with open(filename, "rt") as file:
            self.all_lines: Final[list[str]] = file.read().split("\n")
        self.filename: Final[str] = str(filename)
        self.description: Final[str] = str(description)
        self.issue_line: Final[int] = min(abs(int(issue_line)), len(self.all_lines))

        if self.issue_line < 1 or self.issue_line > len(self.all_lines):
            raise SystemError(
                f"Wrong issue line {issue_line} for file `{filename}`, containing {len(self.all_lines)} lines"
            )

        start_line: int
        end_line: int
        safety_radius: int
        if isinstance(radius_or_range, tuple):
            start_line = max(1, radius_or_range[0])
            end_line = min(len(self.all_lines), radius_or_range[1])
            safety_radius = min(self.issue_line - start_line, end_line - self.issue_line)
        else:
            start_line = max(1, issue_line - radius_or_range)
            end_line = min(len(self.all_lines), issue_line + radius_or_range)
            safety_radius = abs(int(radius_or_range))

        self.start_line: Final[int] = start_line
        self.end_line: Final[int] = end_line
        self.safety_radius: Final[int] = safety_radius
        assert self.start_line <= self.issue_line
        assert self.end_line >= self.issue_line
        assert self.safety_radius >= 0

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
            if proposed_lines[-1].startswith("```"):
                # if new last line is still ``` (this happens if there was "\n" after ```)
                proposed_lines = proposed_lines[:-1]  # remove last line once again

        # remove issue_line_comment if it was added
        issue_line_found: int | None = None
        if self.issue_line_comment is not None:
            for i in range(len(proposed_lines)):
                line: str = proposed_lines[i]
                if line.endswith(self.issue_line_comment):
                    proposed_lines[i] = line[: -len(self.issue_line_comment)]
                    issue_line_found = i
                    break

        result: bool = True
        if try_merging_lines:
            if issue_line_found is not None:
                result = self._merge_from_issue_line(proposed_lines, issue_line_found)
            else:
                result = self._merge_from_both_ends(proposed_lines)
        return result

    def _merge_from_both_ends(self, proposed_lines: list[str]) -> bool:
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

    # NEW FUNCTION
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

        orig_issue_line_index: Final[int] = self.issue_line - self.start_line
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
