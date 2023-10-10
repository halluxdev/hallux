# Copyright: Hallux team, 2023

from __future__ import annotations

import subprocess
from pathlib import Path

from ...auxilary import set_directory
from ...issues.issue import IssueDescriptor
from ..issue_solver import IssueSolver
from ..python.python_issue import PythonIssue


class Ruff_IssueSolver(IssueSolver):
    def __init__(
        self,
        config_path: Path,
        run_path: Path,
        command_dir: str = ".",
        validity_test: str | None = None,
        args: str | None = None,
    ):
        super().__init__(config_path, run_path, command_dir, validity_test=validity_test)

        self.args: str = args if args is not None else "check"

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []
        with set_directory(self.run_path):
            try:
                ruff_output = subprocess.check_output(["ruff", self.args, self.command_dir])
            except subprocess.CalledProcessError as e:
                ruff_output = e.output

        issues.extend(PythonIssue.parseIssues(ruff_output.decode("utf-8")))

        return issues

    def solve_issues(self, diff_target, query_backend):
        print("Process ruff:")
        super().solve_issues(diff_target, query_backend)
