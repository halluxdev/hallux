# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import abstractmethod, ABC
import subprocess
from pathlib import Path
from typing import Final

from processors.set_directory import set_directory
from targets.diff_target import DiffTarget
from backend.query_backend import QueryBackend


class CodeProcessor(ABC):
    def __init__(
        self,
        query_backend: QueryBackend,
        diff_target: DiffTarget,
        run_path: Path,
        base_path: Path,
        config: dict,
        verbose: bool = False,
    ):
        self.query_backend: Final[QueryBackend] = query_backend
        self.diff_target: Final[DiffTarget] = diff_target
        self.config: Final[dict] = config
        self.verbose: Final[bool] = verbose
        self.run_path: Final[Path] = run_path
        self.base_path: Final[Path] = base_path
        success_test = self.config.get("success_test")

        if success_test is not None:
            try:
                with set_directory(self.base_path):
                    subprocess.check_output(
                        ["bash"] + success_test.split(" "),
                    )
            except subprocess.CalledProcessError as e:
                raise SystemError(f"Success Test '{success_test}' is failing right from the start") from e

        self.success_test: Final[str | None] = success_test

    def is_fix_successful(self) -> bool:
        if self.success_test is not None:
            try:
                with set_directory(self.base_path):
                    subprocess.check_output(["bash"] + self.success_test.split(" "))
                if self.verbose:
                    print("\033[92m success test PASSED\033[0m")
                return True
            except subprocess.CalledProcessError:
                if self.verbose:
                    print("\033[91m success test FAILED\033[0m")
                return False

    @abstractmethod
    def process(self):
        pass
