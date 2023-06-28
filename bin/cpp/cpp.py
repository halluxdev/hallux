# Copyright: Hallux team, 2023

from __future__ import annotations

from query_backend import QueryBackend
from diff_target import DiffTarget
from code_processor import CodeProcessor, set_directory
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

        makefile_path: Path

        if "makefile" in self.config.keys():
            makefile_path = Path(self.config["makefile"])
        elif "cmake" in self.config.keys():
            if self.base_path.joinpath("CMakeLists.txt").exists():
                makefile_path = self.cmake_prepare_makefile(str(self.config["cmake"]))
            else:
                print("Cannot find CMakeLists.txt")
                exit(5)
        else:
            print("C++ is enabled, but not `makefile` specified nor 'cmake' was found")
            exit(5)

        if not makefile_path.exists():
            print(f"{str(makefile_path)} does not exist")
            exit(5)

        if "compile" in self.config.keys():
            with set_directory(self.base_path):
                self.solve_make_compile(self.config["compile"], makefile_path)

        if "linking" in self.config.keys():
            self.cpp_linking(self.config["linking"])

    def cmake_prepare_makefile(self, cmake_path: str = ".") -> Path | None:
        if self.base_path.joinpath(cmake_path).joinpath("CMakeLists.txt").exists():
            cmake_path = self.base_path.joinpath(cmake_path)
        elif Path(cmake_path).joinpath("CMakeLists.txt").exists():
            cmake_path = Path(cmake_path)
        else:
            print("Cannot find CMakeLists.txt")
            exit(5)

        makefile_dir = tempfile.mkdtemp(dir="/tmp/hallux")
        os.chdir(makefile_dir)
        try:
            subprocess.check_output(["cmake", f"{str(cmake_path)}"])
            print("CMake initialized succesfully")
        except subprocess.CalledProcessError as e:
            cmake_output = e.output.decode("utf-8")
            print("CMake initialization failed:")
            print(cmake_output)
            exit(5)
            return None

        return Path(makefile_dir).joinpath("Makefile")

    def solve_make_compile(self, params: dict | str, makefile_path: Path):
        makefile_dir: Path = makefile_path.parent

        targets: list[str] = self.list_compile_targets(makefile_dir)

        if self.debug:
            print(f"{len(targets)} targets found")
        target: str
        for target in targets:
            solver = MakeCompile_IssueSolver(target, self.base_path, makefile_dir)
            solver.solve_issues(diff_target=self.diff_target, query_backend=self.query_backend)

    def list_compile_targets(self, makefile_dir: Path):
        with set_directory(makefile_dir):
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
