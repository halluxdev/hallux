# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import ABC, abstractmethod
from issues.issue import IssueDescriptor


class QueryBackend(ABC):
    @abstractmethod
    def query(self, request: str, issue: IssueDescriptor | None = None) -> list[str]:
        pass
