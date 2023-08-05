# Copyright: Hallux team, 2023

from __future__ import annotations
import json
import hashlib

from pathlib import Path
from issues.issue import IssueDescriptor
from backends.query_backend import QueryBackend
from proposals.diff_proposal import DiffProposal


class DummyBackend(QueryBackend):
    def __init__(self, filename: str, base_path: Path, type="dummy", previous_backend: QueryBackend | None = None):
        super().__init__(previous_backend)
        assert type == "dummy"
        self.was_modified: bool = False
        self.base_path = base_path
        self.filename: str

        if Path(filename).is_absolute():
            self.filename = filename
        else:
            self.filename = str(self.base_path.joinpath(filename))

        if Path(self.filename).exists():
            with open(self.filename, "rt") as file:
                self.json = json.load(file)
        else:
            self.json = {}

    def __del__(self):
        if self.was_modified:
            with open(self.filename, "wt") as file:
                json.dump(self.json, file)

    def issue_hash(self, description: str, issue_lines: list[str]) -> str:
        bytes = str(description + "\n" + "\n".join(issue_lines)).encode("utf8")
        return str(hashlib.md5(bytes).hexdigest())

    def query(
        self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] | None = None
    ) -> list[str]:
        if issue is None or issue_lines is None or len(issue_lines) == 0:
            return []

        language = self.json.get(issue.language)
        if language is None:
            return []

        tool = language.get(issue.tool)
        if tool is None:
            return []

        issue_file = Path(issue.filename) if Path(issue.filename).exists() else self.base_path.joinpath(issue.filename)
        found_issues: dict | None = None
        for filename, file_issues in tool.items():
            answer_file = self.base_path.joinpath(filename)
            if issue_file.samefile(answer_file):
                found_issues = file_issues
                break

        if found_issues is None:
            return []

        hash = self.issue_hash(issue.description, issue_lines)

        if hash in found_issues:
            return found_issues[hash]

        return []

    def report_succesfull_fix(self, issue: IssueDescriptor, proposal: DiffProposal) -> None:
        language = self.json.get(issue.language)
        if language is None:
            language = self.json[issue.language] = {}

        tool = language.get(issue.tool)
        if tool is None:
            tool = language[issue.tool] = {}

        issue_file = Path(issue.filename) if Path(issue.filename).exists() else self.base_path.joinpath(issue.filename)
        found_issues: dict | None = None
        for filename, file_issues in tool.items():
            answer_file = self.base_path.joinpath(filename)
            if issue_file.samefile(answer_file):
                found_issues = file_issues
                break

        if found_issues is None:
            found_issues = tool[issue.filename] = {}

        hash = self.issue_hash(issue.description, proposal.issue_lines)

        if hash not in found_issues:
            found_issues[hash] = "\n".join(proposal.proposed_lines)

        self.was_modified = True

        if self.previous is not None:
            self.previous.report_succesfull_fix(issue, proposal)
