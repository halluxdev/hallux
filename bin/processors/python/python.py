# Copyright: Hallux team, 2023

from __future__ import annotations
from backend.query_backend import QueryBackend
from targets.diff_target import DiffTarget
from processors.code_processor import CodeProcessor
from processors.set_directory import set_directory
from pathlib import Path
from processors.python.ruff import Ruff_IssueSolver


class PythonProcessor(CodeProcessor):
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
        print("Process Python issues:")
        with set_directory(self.run_path):
            if "ruff" in self.config.keys():
                self.python_ruff(self.config["ruff"])

    def python_ruff(self, config):
        with set_directory(self.run_path):
            solver = Ruff_IssueSolver(config)
            solver.solve_issues(diff_target=self.diff_target, query_backend=self.query_backend)
