# Copyright: Hallux team, 2023

from __future__ import annotations
from query_backend import QueryBackend
from diff_target import DiffTarget
from code_processor import CodeProcessor, set_directory
from pathlib import Path
from python.ruff import Ruff_IssueSolver


class PythonProcessor(CodeProcessor):
    def __init__(
        self, query_backend: QueryBackend, diff_target: DiffTarget, base_path: Path, config: dict, debug: bool = False
    ):
        super().__init__(query_backend, diff_target, config, debug)
        self.base_path: Path = base_path

    def process(self) -> None:
        print("Process Python issues:")
        with set_directory(self.base_path):
            if "ruff" in self.config.keys():
                self.python_ruff(self.config["ruff"])

            if "tests" in self.config.keys():
                self.python_tests(self.config["tests"])

            if "docstrings" in self.config:
                self.python_docstrings(self.config["docstrings"])

    def python_ruff(self, config):
        solver = Ruff_IssueSolver(config)
        solver.solve_issues(diff_target=self.diff_target, query_backend=self.query_backend)

    def python_tests(self, params: dict | str):
        pass

    def python_docstrings(self, params: dict | str):
        pass
