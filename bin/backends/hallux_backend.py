# Copyright: Hallux team, 2023

from __future__ import annotations
from issues.issue import IssueDescriptor
from backends.query_backend import QueryBackend


class HalluxBackend(QueryBackend):
    def __init__(self, url: str, token: str | None = None, type="hallux", previous_backend: QueryBackend | None = None):
        super().__init__(previous_backend)
        assert type == "hallux"
        self.url = url
        self.token = token

    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:
        return []
