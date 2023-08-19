# Copyright: Hallux team, 2023

from __future__ import annotations

import subprocess

from issues.issue import IssueDescriptor
from issues.issue_solver import IssueSolver
from issues.python_issue import PythonIssue


class Mypy_IssueSolver(IssueSolver):
    def __init__(self, mypy_args: str | None = None):
        super().__init__()
        self.mypy_args: str = mypy_args if mypy_args is not None else "--ignore-missing-imports ."

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []
        try:
            mypy_output = subprocess.check_output(["mypy", self.mypy_args])
        except subprocess.CalledProcessError as e:
            mypy_output = e.output

        issues.extend(PythonIssue.parseIssues(mypy_output.decode("utf-8"), tool="mypy", keyword="error:"))

        return issues
