# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path
from auxilary import set_directory

from backends.query_backend import QueryBackend
from processors.code_processor import CodeProcessor
from processors.eslint.eslint_issue_solver import EslintIssueSolver
from targets.diff_target import DiffTarget

class EslintProcessor(CodeProcessor):
    def __init__(
        self,
        query_backend: QueryBackend,
        diff_target: DiffTarget,
        run_path: Path,
        base_path: Path,
        config: dict,
        verbose: bool = False,
    ):
        super().__init__(query_backend, diff_target, run_path, base_path, config, verbose)

    def process(self) -> None:
        print("Process Eslint issues:")
        with set_directory(self.run_path):
            solver = EslintIssueSolver(self.config)
            solver.solve_issues(diff_target=self.diff_target, query_backend=self.query_backend)

