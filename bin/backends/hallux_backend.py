# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path

from backends.query_backend import QueryBackend
from issues.issue import IssueDescriptor


class HalluxBackend(QueryBackend):
    def __init__(
        self,
        url: str,
        token: str | None = None,
        type="hallux",
        base_path: Path = Path(),
        previous_backend: QueryBackend | None = None,
        verbose: bool = False,
    ):
        super().__init__(base_path, previous_backend, verbose=verbose)
        assert type == "hallux"
        self.url = url
        self.token = token

    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:
        return []
