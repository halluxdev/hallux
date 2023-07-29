# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import abstractmethod
import subprocess
from pathlib import Path
from typing import Final

from targets.diff_target import DiffTarget
from backend.query_backend import QueryBackend


class CodeProcessor:
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
        if (
            success_test is not None
            and not Path(success_test).is_absolute()
            and self.base_path.joinpath(success_test).exists()
        ):
            success_test = str(self.base_path.joinpath(success_test))
        self.success_test: Final[str | None] = success_test

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
