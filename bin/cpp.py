#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations
from query_backend import QueryBackend
from diff_target import DiffTarget
from code_processor import CodeProcessor
import subprocess
import os
import tempfile
from pathlib import Path


class CppProcessor(CodeProcessor):
    def __init__(
        self, query_backend: QueryBackend, diff_target: DiffTarget, base_path: Path, config: dict, debug: bool = False
    ):
        self.query_backend: QueryBackend = query_backend
        self.diff_target: DiffTarget = diff_target
        self.base_path: Path = base_path
        self.config = config
        self.debug: bool = debug

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
            self.cpp_compile(self.config["compile"], makefile_dir)
        if "linking" in self.config.keys():
            self.cpp_linking(self.config["linking"])
        if "tests" in self.config.keys():
            self.cpp_tests(self.config["tests"])

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

    def cpp_compile(self, params: dict | str, makefile_dir: Path):
        os.chdir(str(makefile_dir))
        make_output = subprocess.check_output(["make", "help"])
        targets: list[str] = str(make_output.decode("utf-8")).split("\n")
        target: str
        for target in targets:
            if target.endswith(".o"):
                target = target.lstrip(".")
                target = target.lstrip(" ")
                self.compile_make_target(target)

    # def find_cpp_file(self, make_target: str) -> Path | None:
    #     make_target = make_target[:-2]
    #     target_list : list[str] = make_target.split("/")
    #     path = self.base_path
    #     while len(target_list) > 1:
    #         if path.joinpath(target_list[0]).exists():
    #             path = path.joinpath(target_list[0])
    #             target_list = target_list[1:]
    #
    #     if isinstance(target_list, list):
    #         target_name = target_list[0]
    #     else:
    #         target_name = target_list
    #
    #     repo_files: list[str] = os.listdir(str(path))
    #     for filename in repo_files:
    #         if filename.startswith(target_name):
    #             return path.joinpath(filename)
    #
    #     return None

    def parse_compilation_error(self, make_output: str) -> tuple[list[list[str]], list[list[str]]]:
        output_lines: list[str] = make_output.split("\n")
        errors: list[list[str]] = []
        warnings: list[list[str]] = []
        err_amount: int = 0
        warn_amount: int = 0
        error: list[str] | None = None
        warning: list[str] | None = None

        for line_num in range(len(output_lines)):
            err_line_list = output_lines[line_num].split(":")
            # if re.match("^/([a-zA-Z0-9/_]).cpp:([0-9]):([0-9]): error: ", output_lines[line_num]):
            if (
                len(err_line_list) > 4
                and err_line_list[3] == " error"
                and err_line_list[1].isdecimal()
                and err_line_list[2].isdecimal()
            ):
                if error is not None:
                    error = error[:-1]
                    errors.append(error)
                    error = None
                if warning is not None:
                    warning = warning[:-1]
                    warnings.append(warning)
                    warning = None

                err_amount += 1
                print(output_lines[line_num])
                error = [output_lines[line_num - 1]] if line_num > 0 else []
                error.append(output_lines[line_num])
            elif (
                len(err_line_list) > 4
                and err_line_list[3] == " warning"
                and err_line_list[1].isdecimal()
                and err_line_list[2].isdecimal()
            ):
                if error is not None:
                    error = error[:-1]
                    errors.append(error)
                    error = None
                if warning is not None:
                    warning = warning[:-1]
                    warnings.append(warning)
                    warning = None
                warn_amount += 1
                print(output_lines[line_num])
                warning = [output_lines[line_num - 1]] if line_num > 0 else []
                warning.append(output_lines[line_num])
            elif error is not None:
                error.append(output_lines[line_num])
            elif warning is not None:
                warning.append(output_lines[line_num])

        print(f"{err_amount} errors , {warn_amount} warnings found")
        return errors, warnings

    def compile_make_target(self, target) -> int:
        try:
            subprocess.check_output(["make", target], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            make_output: str = e.output.decode("utf-8")
            print("Compilation errors found:")
            # print(make_output)
            # erroneous_file = self.find_cpp_file(target)
            # print(f"Corresponding file: {erroneous_file}")

            errors, warnings = self.parse_compilation_error(make_output)

            for error in errors:
                props = error[1].split(":")
                filename = props[0]
                err_line: int = int(props[1])
                added_comment = f" // {err_line}"
                start_line, end_line, warnlines, filelines = self.read_lines(filename, err_line, 4, added_comment)
                print(error)

                request = "Fix gcc compilation issue, write resulting code only:\n"
                for line in error:
                    request = request + line + "\n"

                request = request + "Excerpt from the corresponding cpp file (not full):\n"

                for line in warnlines:
                    request = request + line + "\n"

                print("request")
                print(request)
                result: list[str]
                if self.debug:
                    result = [
                        "void print_usage(char* argv[])\n{\n"
                        + '  std::cout << "Usage: " << argv[0] << " filename.cpp" << std::endl;\n'
                        + '  return; // fix the error by removing "1"\n}\n\n'
                        + "int main(int argc, char* argv[])\n{"
                    ]
                else:
                    result = self.query_backend.query(request)
                print("result")
                print(result)

                if len(result) > 0:
                    resulting_lines = self.prepare_lines(result[0], added_comment)

                    self.diff_target.apply_diff(filename, start_line, end_line, resulting_lines, error[1])

                if self.debug:
                    break

        return 0

    def cpp_linking(self, params: dict | str):
        pass

    def cpp_tests(self, params: dict | str):
        pass
