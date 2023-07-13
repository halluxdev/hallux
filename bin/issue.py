# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Final
from file_diff import FileDiff


class IssueDescriptor(ABC):
    def __init__(self, tool: str, filename: str, issue_line: int = 0, description: str = "", issue_type : str = "warning", language: str | None = None):

        self.tool: Final[str] = tool
        self.filename: Final[str] = filename
        self.issue_line: int = issue_line
        self.description: str = description
        self.message_lines: list[str] = []
        self.file_diff: FileDiff | None = None
        self.issue_type : str = issue_type

        if language is None:
            if filename.endswith(".py"):
                language="python"
            elif filename.endswith(".cpp") or filename.endswith(".hpp") or filename.endswith(".c") or filename.endswith(".h"):
                language="cpp"
            elif filename.endswith(".js") or filename.endswith(".ts"):
                language="js"
            else:
                language = "programming"

        self.language: Final[str] = language

    @abstractmethod
    def try_fixing(self, query_backend, diff_target) -> bool:
        pass
