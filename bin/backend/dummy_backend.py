# Copyright: Hallux team, 2023

from __future__ import annotations
import json
from pathlib import Path
from issue import IssueDescriptor
from backend.query_backend import QueryBackend


class DummyBackend(QueryBackend):
    def __init__(self, filename: str, root_path: Path):
        self.base_path = root_path
        self.filename: str
        self.save_on_exit = False
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

    def __del__(self):
        if self.save_on_exit:
            with open(self.filename, "wt") as file:
                json.dump(self.json, file)

    def query(self, request: str, issue: IssueDescriptor | None = None) -> list[str]:
        if issue is None:
            return []

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

        if issue.description in found_issues:
            return found_issues[issue.description]
        elif issue.file_diff is not None:
            dummy_answer = found_issues[issue.description] = ["\n".join(issue.file_diff.issue_lines)]
            return dummy_answer

        return []
