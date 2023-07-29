# Copyright: Hallux team, 2023

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Final

from backend.query_backend import QueryBackend
from targets.diff_target import DiffTarget
from processors.code_processor import CodeProcessor
from processors.set_directory import set_directory
from processors.cpp.make_compile import MakeCompile_IssueSolver
import subprocess
import os
import tempfile
from pathlib import Path


@dataclass
class CompileTarget:
    target: str
    makefile_dir: Path


class CppProcessor(CodeProcessor):
    makefile: Final[str] = "Makefile"
    cmakelists: Final[str] = "CMakeLists.txt"

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
        print("Process C++ issues:")

        makefile_path: Path
        # Try some options for searching Makefile / CMakelists.txt
        if self.base_path.joinpath(self.makefile).exists():
            makefile_path = self.base_path.joinpath(self.makefile)
        elif self.base_path.joinpath("build", self.makefile).exists():
            makefile_path = self.base_path.joinpath("build", self.makefile)
        elif self.base_path.joinpath(self.cmakelists).exists():
            makefile_path = self.makefile_from_cmake(str(self.base_path))
        elif self.base_path.parent.joinpath(self.cmakelists).exists():
            makefile_path = self.makefile_from_cmake(str(self.base_path.parent))
        else:
            print("C++ is enabled, but cannot `Makefile` nor 'CMakeLists.txt'")
            return

        # if "compile" in self.config.keys():
        with set_directory(self.base_path):
            self.solve_make_compile(self.config["compile"], makefile_path)

        if "linking" in self.config.keys():
            self.cpp_linking(self.config["linking"])

    def makefile_from_cmake(self, cmake_path: str = ".") -> Path | None:
        Path("/tmp/hallux").mkdir(exist_ok=True)
        makefile_dir = tempfile.mkdtemp(dir="/tmp/hallux")
        os.chdir(makefile_dir)
        try:
            subprocess.check_output(["cmake", f"{str(cmake_path)}"])
            print("CMake initialized succesfully")
        except subprocess.CalledProcessError as e:
            cmake_output = e.output.decode("utf-8")
            print(cmake_output, file=sys.stderr)
            raise SystemError("CMake initialization failed") from e

        return Path(makefile_dir).joinpath(self.makefile)

    def solve_make_compile(self, params: dict | str, makefile_path: Path):
        makefile_dir: Path = makefile_path.parent

        compile_targets: list[CompileTarget] = []
        self.list_compile_targets(makefile_dir, compile_targets)

        if self.verbose:
            print(f"{len(compile_targets)} targets found")
        target: CompileTarget
        for target in compile_targets:
            solver = MakeCompile_IssueSolver(target.target, target.makefile_dir, self.verbose)
            solver.solve_issues(diff_target=self.diff_target, query_backend=self.query_backend)

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

    def cpp_linking(self, params: dict | str):
        """
        Add a nested comment explaining why this method is empty
        """
        pass

