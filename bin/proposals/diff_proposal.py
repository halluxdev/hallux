# Copyright: Hallux team, 2023

from __future__ import annotations

from abc import ABC, abstractmethod


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
        self.proposed_lines: list[str] = []

    @abstractmethod
    def try_fixing(self, query_backend, diff_target) -> bool:
        pass
