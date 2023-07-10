# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Final
from file_diff import FileDiff


class IssueDescriptor(ABC):
    def __init__(self, language: str, tool: str, filename: str, issue_line: int = 0, description: str = ""):
        self.language: Final[str] = language
        self.tool: Final[str] = tool
        self.filename: Final[str] = filename
        self.issue_line: int = issue_line
        self.description: str = description
        self.message_lines: list[str] = []
        self.file_diff: FileDiff | None = None

    @abstractmethod
    def try_fixing(self, query_backend, diff_target) -> bool:
        pass
