# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import abstractmethod
import subprocess
from contextlib import contextmanager
from pathlib import Path
import os

from targets.diff_target import DiffTarget
from backend.query_backend import QueryBackend


@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """
    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


class CodeProcessor:
    def __init__(self, query_backend: QueryBackend, diff_target: DiffTarget, config: dict, verbose: bool = False):
        self.query_backend: QueryBackend = query_backend
        self.diff_target: DiffTarget = diff_target
        self.config = config
        self.verbose: bool = verbose
        self.success_test = self.config.get("success_test")

    def is_fix_successful(self) -> bool:
        if self.success_test is not None:
            try:
                if self.verbose:
                    print(f"RUN success_test: {self.success_test}")
                subprocess.check_output([self.success_test])
                if self.verbose:
                    print("success_test OK")
                return True
            except subprocess.CalledProcessError:
                if self.verbose:
                    print("success_test FAILED")
                return False

    @abstractmethod
    def process(self):
        pass
