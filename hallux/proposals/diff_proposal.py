# Copyright: Hallux team, 2023

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DiffProposal(ABC):
    # This class does not contain any fancy members like IssueDescriptor to avoid circular imports
    def __init__(
        self, filename: str = "", description: str = "", issue_line: int = 0, start_line: int = 0, end_line: int = 0
    ):
        self.filename: str = filename
        self.description: str = description
        self.issue_line: int = issue_line
        self.start_line: int = start_line
        self.end_line: int = end_line
        self.all_lines: list[str] = []
        self.issue_lines: list[str] = []
        self.proposed_lines: list[str] = []

    @abstractmethod
    def try_fixing(self, query_backend, diff_target) -> bool:
        pass

    def try_fixing_with_priority(self, query_backend, diff_target, used_backend) -> tuple[bool, Any]:
        previous_backend = query_backend.previous_backend()

        if previous_backend is not None and previous_backend != used_backend:
            return self.try_fixing_with_priority(previous_backend, diff_target, used_backend)
        else:
            return self.try_fixing(query_backend, diff_target), query_backend
