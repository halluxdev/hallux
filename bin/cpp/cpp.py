#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from query_backend import QueryBackend
from diff_target import DiffTarget
from code_processor import CodeProcessor
from cpp.make_compile import MakeCompile_IssueSolver
import subprocess
import os
import tempfile
from pathlib import Path


class CppProcessor(CodeProcessor):
    def __init__(
        self, query_backend: QueryBackend, diff_target: DiffTarget, base_path: Path, config: dict, debug: bool = False
    ):
        super().__init__(query_backend, diff_target, config, debug)
        self.base_path: Path = base_path

    def process(self) -> None:
        print("Process C++ issues:")
        makefile_dir: Path
        if "makefile_dir" in self.config.keys():
            makefile_dir = Path(self.config["makefile_dir"])
        elif self.base_path.joinpath("CMakeLists.txt").exists():
            makefile_dir = Path(self.prepare_makefile_dir())
        else:
            print("C++ is enabled, but not `makefile_dir` specified nor CMakeLists.txt was found")
            return

        if not makefile_dir.joinpath("Makefile"):
            print(f"{str(makefile_dir.joinpath('Makefile'))} does not exist")
            return

        if "compile" in self.config.keys():
            self.solve_make_compile(self.config["compile"], makefile_dir)

        if "linking" in self.config.keys():
            self.cpp_linking(self.config["linking"])

    def prepare_makefile_dir(self) -> str | None:
        makefile_dir = tempfile.mkdtemp(dir="/tmp/hallux")
        os.chdir(makefile_dir)
        try:
            subprocess.check_output(["cmake", f"{str(self.base_path)}"])
            print("CMake initialized succesfully")
        except subprocess.CalledProcessError as e:
            cmake_output = e.output.decode("utf-8")
            print("CMake initialization failed:")
            print(cmake_output)
            exit(5)
            return None

        return makefile_dir

    def solve_make_compile(self, params: dict | str, makefile_dir: Path):
        os.chdir(str(makefile_dir))
        targets: list[str] = self.list_compile_targets(params)
        if self.debug:
            print(f"{len(targets)} targets found")
        target: str
        for target in targets:
            solver = MakeCompile_IssueSolver(target)
            solver.solve_issues(diff_target=self.diff_target, query_backend=self.query_backend)

    def list_compile_targets(self, params: dict | str):
        make_output = subprocess.check_output(["make", "help"])
        targets: list[str] = str(make_output.decode("utf-8")).split("\n")
        output_targets: list[str] = []
        target: str
        for target in targets:
            if target.endswith(".o"):
                target = target.lstrip(".")
                target = target.lstrip(" ")
                output_targets.append(target)
        return output_targets

    def cpp_linking(self, params: dict | str):
        pass
