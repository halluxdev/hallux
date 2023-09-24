# Copyright: Hallux team, 2023

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..backends.query_backend import QueryBackend
from ..issues.issue import IssueDescriptor
from ..proposals.diff_proposal import DiffProposal


class DummyBackend(QueryBackend):
    def __init__(
        self,
        filename: str,
        base_path: Path,
        type="dummy",
        previous_backend: QueryBackend | None = None,
    ):
        assert type == "dummy"
        super().__init__(base_path, previous_backend)

        self.filename: str
        self.was_modified: bool = False
        if Path(filename).is_absolute():
            self.filename = filename
        else:
            self.filename = str(self.base_path.joinpath(filename))

        if Path(self.filename).exists():
            with open(self.filename, "rt") as file:
                self.json = json.load(file)
        else:
            self.json = {}
            self.save_on_exit = True

    def issue_hash(self, description: str, issue_lines: list[str]) -> str:
        bytes = str(description + "\n" + "\n".join(issue_lines)).encode("utf8")
        return str(hashlib.md5(bytes).hexdigest())

    def __del__(self):
        if self.was_modified:
            with open(self.filename, "wt") as file:
                json.dump(self.json, file)

    def report_succesfull_fix(self, issue: IssueDescriptor, proposal: DiffProposal) -> None:
        hash = self.issue_hash(issue.description, proposal.issue_lines)

        if hash not in self.json:
            self.json[hash] = "\n".join(proposal.proposed_lines)

        self.was_modified = True

        if self.previous is not None:
            self.previous.report_succesfull_fix(issue, proposal)

    def query(
        self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] | None = None
    ) -> list[str]:
        if issue is not None and issue_lines is not None:
            hash = self.issue_hash(issue.description, issue_lines)
            return self.json.get(hash, [])

        return []
