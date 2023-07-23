# Copyright: Hallux team, 2023

from __future__ import annotations

from abc import ABC, abstractmethod

# from backend.query_backend import QueryBackend
# from targets.diff_target import DiffTarget


class DiffProposal(ABC):
    def __init__(self, filename: str = "", description: str = "", start_line: int = 0, end_line: int = 0):
        self.filename: str = filename
        self.description: str = description
        self.start_line: int = start_line
        self.end_line: int = end_line
        self.all_lines: list[str] = []
        self.proposed_lines: list[str] = []

    @abstractmethod
    def try_fixing(self, query_backend, diff_target) -> bool:
        pass
