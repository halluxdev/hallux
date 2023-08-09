# Copyright: Hallux team, 2023

from __future__ import annotations
import subprocess

from issues.issue import IssueDescriptor
from issues.issue_solver import IssueSolver
from issues.python_issue import PythonIssue


class Ruff_IssueSolver(IssueSolver):
    def __init__(self, ruff_dir: str | None = None):
        super().__init__()
        self.ruff_dir: str = ruff_dir if ruff_dir is not None else "."

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []
        try:
            ruff_output = subprocess.check_output(["ruff", "check", self.ruff_dir])
        except subprocess.CalledProcessError as e:
            ruff_output = e.output

        issues.extend(PythonIssue.parseIssues(ruff_output.decode("utf-8")))

        return issues
