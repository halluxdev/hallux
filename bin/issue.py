# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Final
import copy

# from query_backend import QueryBackend
# from diff_target import DiffTarget


class IssueDescriptor(ABC):
    def __init__(self, language: str, tool: str, filename: str, issue_line: int = 0, description: str = ""):
        self.language: Final[str] = language
        self.tool: Final[str] = tool
        self.filename: Final[str] = filename
        self.issue_line: int = issue_line
        self.description: str = description
        self.message_lines: list[str] = []
        self.debug: bool = False

    @abstractmethod
    def try_fixing(self, query_backend, diff_target):
        pass

    @staticmethod
    def read_lines(
        filename: str, line: int, raidus: int, add_line_comment: str | None = None
    ) -> tuple[int, int, list[str], list[str]]:
        with open(filename, "rt") as file:
            filelines = file.read().split("\n")
        start_line = max(0, line - raidus)
        end_line = min(len(filelines) - 1, line + raidus)
        requested_lines = copy.deepcopy(filelines[start_line:end_line])
        if add_line_comment is not None:
            requested_lines[line - start_line] += add_line_comment
        return start_line, end_line, requested_lines, filelines

    @staticmethod
    def prepare_lines(query_result: str, remove_line_comment: str | None = None) -> list[str]:
        resulting_lines = query_result.split("\n")
        for i in range(len(resulting_lines)):
            line: str = resulting_lines[i]
            if remove_line_comment is not None and line.endswith(remove_line_comment):
                resulting_lines[i] = line[: -len(remove_line_comment)]
                break
        return resulting_lines
