# Copyright: Hallux team, 2023

from __future__ import annotations

import subprocess

from issues.issue import IssueDescriptor
from issues.issue_solver import IssueSolver
from issues.eslint_issue import EslintIssue


class EslintIssueSolver(IssueSolver):
    def __init__(self, config: dict | None = None):
        super().__init__(config.get("command"))
        self.command: str = config.get("command")

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []

        print("Running command: " + self.command)

        try:
            output = subprocess.check_output(self.command.split())
        except subprocess.CalledProcessError as e:
            output = e.output

        issues.extend(EslintIssue.parseIssues(output.decode("utf-8"), keyword="warning"))

        return issues
