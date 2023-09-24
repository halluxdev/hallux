# Copyright: Hallux team, 2023

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Final

from ..issues.issue import IssueDescriptor


class QueryBackend(ABC):
    def __init__(self, base_path: Path = Path(), previous_backend: QueryBackend | None = None):
        self.previous = previous_backend
        self.base_path: Final[Path] = base_path
        self.was_modified = False

    def previous_backend(self) -> QueryBackend | None:
        return self.previous

    @abstractmethod
    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:
        pass

    def report_succesfull_fix(self, issue, proposal) -> None:
        if self.previous is not None:
            self.previous.report_succesfull_fix(issue, proposal)
