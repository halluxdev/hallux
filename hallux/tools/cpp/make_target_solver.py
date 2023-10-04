# Copyright: Hallux team, 2023

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Final

from hallux.logger import logger

from ...auxilary import set_directory
from ...backends.query_backend import QueryBackend
from ...issues.issue import IssueDescriptor
from ...targets.diff import DiffTarget
from ...tools.cpp.issue import CppIssue
from ...tools.issue_solver import IssueSolver


class MakeTargetSolver(IssueSolver):
    def __init__(self, run_path: Path, make_target: str, config_path: Path = Path()):
        super().__init__(config_path=config_path, run_path=run_path)
        # self.makefile_dir: Final[Path] = makefile_dir
        self.make_target: Final[str] = make_target

    def solve_issues(self, diff_target: DiffTarget, query_backend: QueryBackend):
        logger.info(f"{self.run_path}/Makefile : '{self.make_target}'")
        with set_directory(self.run_path):
            super().solve_issues(diff_target, query_backend)

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []

        with set_directory(self.run_path):
            try:
                subprocess.check_output(["make", self.make_target], stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                make_output: str = e.output.decode("utf-8")
                issues.extend(CppIssue.parseMakeIssues(make_output))

        return issues
