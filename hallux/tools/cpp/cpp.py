# Copyright: Hallux team, 2023

from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from hallux.logger import logger

from ...auxilary import set_directory
from ...backends.query_backend import QueryBackend
from ...issues.issue import IssueDescriptor
from ...targets.diff import DiffTarget
from .make_target_solver import IssueSolver, MakeTargetSolver


@dataclass
class CompileTarget:
    target: str
    makefile_dir: Path


class Cpp_IssueSolver(IssueSolver):
    makefile: Final[str] = "Makefile"
    cmakelists: Final[str] = "CMakeLists.txt"

    def __init__(
        self,
        config_path: Path,
        run_path: Path,
        command_dir: str = ".",
        validity_test: str | None = None,
    ):
        super().__init__(config_path, run_path, command_dir, validity_test=validity_test)
        self.tmp_dir: tempfile.TemporaryDirectory | None = None

    def list_issues(self) -> list[IssueDescriptor]:
        return []

    def solve_issues(self, diff_target: DiffTarget, query_backend: QueryBackend):
        makefile_path: Path
        # Try some options for searching Makefile / CMakelists.txt
        if self.run_path.joinpath(self.command_dir, self.makefile).exists():
            # command_dir/Makefile
            makefile_path = self.run_path.joinpath(self.makefile)
        elif self.run_path.joinpath("build", self.makefile).exists():
            # if command_dir/build/Makefile
            makefile_path = self.run_path.joinpath("build", self.makefile)
        elif self.run_path.joinpath(self.command_dir, self.cmakelists).exists():
            # command_dir/CMakeLists.txt
            makefile_path = self.makefile_from_cmake(self.run_path.joinpath(self.command_dir))
        else:
            logger.error("Process C/C++: cannot find `Makefile` nor 'CMakeLists.txt'")
            return
        print("Process C/C++:")

        with set_directory(makefile_path.parent):
            self.solve_make_compile(diff_target, query_backend, makefile_path)

    def makefile_from_cmake(self, cmake_path: Path) -> Path | None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        with set_directory(Path(self.tmp_dir.name)):
            try:
                subprocess.check_output(["cmake", f"{str(cmake_path)}"])
                logger.info("CMake initialized successfully")
            except subprocess.CalledProcessError as e:
                cmake_output = e.output.decode("utf-8")
                logger.error(cmake_output)
                raise SystemError("CMake initialization failed") from e

            return Path(self.tmp_dir.name).joinpath(self.makefile)

    def solve_make_compile(self, diff_target: DiffTarget, query_backend: QueryBackend, makefile_path: Path):
        makefile_dir: Path = makefile_path.parent

        compile_targets: list[CompileTarget] = []
        self.list_compile_targets(makefile_dir, compile_targets)

        logger.info(f"{len(compile_targets)} Makefile targets found")
        target: CompileTarget
        for target in compile_targets:
            solver = MakeTargetSolver(run_path=target.makefile_dir, make_target=target.target)
            solver.solve_issues(diff_target=diff_target, query_backend=query_backend)

    def list_compile_targets(self, makefile_dir: Path, compile_targets: list[CompileTarget]):
        with set_directory(makefile_dir):
            try:
                make_output = subprocess.check_output(["make", "help"])
            except subprocess.CalledProcessError as e:
                raise SystemError(e.output.decode("utf8")) from e

            targets: list[str] = str(make_output.decode("utf-8")).split("\n")

            target: str
            for target in targets:
                if target.endswith(".o"):
                    target = target.lstrip(".")
                    target = target.lstrip(" ")
                    compile_targets.append(CompileTarget(target=target, makefile_dir=makefile_dir))

            inner_dirs: list = os.listdir(makefile_dir)

            for inner_dir in inner_dirs:
                inner_makefile = makefile_dir.joinpath(str(inner_dir), "Makefile")
                if inner_makefile.exists():
                    self.list_compile_targets(makefile_dir.joinpath(str(inner_dir)), compile_targets)
