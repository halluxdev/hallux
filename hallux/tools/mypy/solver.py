# Copyright: Hallux team, 2023

from __future__ import annotations

import subprocess
from pathlib import Path

from ...auxilary import set_directory
from ...issues.issue import IssueDescriptor
from ...tools.issue_solver import IssueSolver
from ...tools.python.python_issue import PythonIssue


class Mypy_IssueSolver(IssueSolver):
    def __init__(
        self,
        config_path: Path,
        run_path: Path,
        command_dir: str = ".",
        validity_test: str | None = None,
        args: str | None = None,
    ):
        super().__init__(config_path, run_path, command_dir, validity_test=validity_test)
        self.args: str = args if args is not None else "--ignore-missing-imports"

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []

        with set_directory(self.run_path):
            try:
                mypy_output = subprocess.check_output(["mypy", self.args, self.command_dir])
            except subprocess.CalledProcessError as e:
                mypy_output = e.output

        issues.extend(PythonIssue.parseIssues(mypy_output.decode("utf-8"), tool="mypy", keyword="error:"))

        return issues

    def solve_issues(self, diff_target, query_backend):
        print("Process mypy:")
        super().solve_issues(diff_target, query_backend)
