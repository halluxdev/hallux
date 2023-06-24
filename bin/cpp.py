#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from query_backend import QueryBackend
from diff_target import DiffTarget
from code_processor import CodeProcessor
from issue import IssueDescriptor
import subprocess
import os
import tempfile
from pathlib import Path


class CppIssueDescriptor(IssueDescriptor):
    def __init__(self, filename: str, issue_line: int = 0, description: str = ""):
        super().__init__(
            language="cpp", tool="compile", filename=filename, issue_line=issue_line, description=description
        )

    def try_fixing(self, query_backend: QueryBackend, diff_target: DiffTarget):
        request = "Fix gcc compilation issue, write resulting code only:\n"
        for line in self.message_lines:
            request = request + line + "\n"
        request = request + "Excerpt from the corresponding cpp file (not full):\n"
        line_comment: str = f" // line {str(self.issue_line)}"
        start_line, end_line, requested_codelines, _ = CodeProcessor.read_lines(
            self.filename, self.issue_line, 4, line_comment
        )
        for line in requested_codelines:
            request = request + line + "\n"
        result: list[str] = query_backend.query(request, self)

        if self.debug:
            print("request")
            print(request)
            print("result")
            print(result)

        if len(result) > 0:
            resulting_lines = CodeProcessor.prepare_lines(result[0], line_comment)
            diff_target.apply_diff(self.filename, start_line, end_line, resulting_lines, self.description)

    @staticmethod
    def parseMakeIssues(make_output: str, debug: bool = False) -> list[CppIssueDescriptor]:
        issues: list[CppIssueDescriptor] = []
        output_lines: list[str] = make_output.split("\n")
        current_issue: CppIssueDescriptor | None = None

        for line_num in range(len(output_lines)):
            err_line_list = output_lines[line_num].split(":")
            if (
                len(err_line_list) > 4
                and Path(err_line_list[0]).exists()
                and err_line_list[1].isdecimal()
                and err_line_list[2].isdecimal()
                and (err_line_list[3] == " error" or err_line_list[3] == " warning")
            ):
                if current_issue is not None:
                    current_issue.message_lines = current_issue.message_lines[:-1]
                    issues.append(current_issue)

                current_issue = CppIssueDescriptor(
                    filename=err_line_list[0],
                    issue_line=int(err_line_list[1]),
                    description=str(":".join(err_line_list[4:]).lstrip(" ")),
                )
                current_issue.message_lines = [output_lines[line_num - 1]] if line_num > 0 else []
                current_issue.message_lines.append(output_lines[line_num])
                current_issue.debug = debug

            elif current_issue is not None:
                current_issue.message_lines.append(output_lines[line_num])

        if current_issue is not None:
            issues.append(current_issue)

        return issues


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
            self.process_compile_issues_reqursively(self.config["compile"], makefile_dir)
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

    def process_compile_issues_reqursively(self, params: dict | str, makefile_dir: Path):
        os.chdir(str(makefile_dir))
        targets: list[str] = self.list_compile_targets(params)
        if self.debug:
            print(f"{len(targets)} targets found")
        target: str
        for target in targets:
            target_issues: list[CppIssueDescriptor] = self.list_target_issues(target)
            if self.debug:
                print(f"{len(target_issues)} in target '{target}' found")

            issue_index: int = 0
            while issue_index < len(target_issues):
                issue = target_issues[issue_index]
                issue.try_fixing(diff_target=self.diff_target, query_backend=self.query_backend)
                new_target_issues: list[CppIssueDescriptor] = self.list_target_issues(target)

                if len(new_target_issues) < len(target_issues):
                    # Number of issues decreased => FIX SUCCESFULL
                    self.diff_target.commit_diff()
                    target_issues = new_target_issues
                    print(f"{issue.filename}:{issue.issue_line}: {issue.description} : SUCCESSFULLY FIXED")
                    # Do not touch issue_index
                else:
                    self.diff_target.revert_diff()
                    issue_index += 1
                    print(f"{issue.filename}:{issue.issue_line}: {issue.description} : unable to fix")

                if self.debug:
                    break

            if self.debug:
                break

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

    def list_target_issues(self, target: str) -> list[CppIssueDescriptor]:
        issues: list[CppIssueDescriptor] = []
        try:
            subprocess.check_output(["make", target], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            make_output: str = e.output.decode("utf-8")
            # print("Compilation errors found:")
            issues.extend(CppIssueDescriptor.parseMakeIssues(make_output, self.debug))

        return issues

    # def cpp_compile(self, params: dict | str, makefile_dir: Path):
    #     os.chdir(str(makefile_dir))
    #     make_output = subprocess.check_output(["make", "help"])
    #     targets: list[str] = str(make_output.decode("utf-8")).split("\n")
    #     target: str
    #     for target in targets:
    #         if target.endswith(".o"):
    #             target = target.lstrip(".")
    #             target = target.lstrip(" ")
    #             self.compile_make_target(target)
    #
    # def parse_compilation_error(self, make_output: str) -> tuple[list[list[str]], list[list[str]]]:
    #     output_lines: list[str] = make_output.split("\n")
    #     errors: list[list[str]] = []
    #     warnings: list[list[str]] = []
    #     err_amount: int = 0
    #     warn_amount: int = 0
    #     error: list[str] | None = None
    #     warning: list[str] | None = None
    #
    #     for line_num in range(len(output_lines)):
    #         err_line_list = output_lines[line_num].split(":")
    #         # if re.match("^/([a-zA-Z0-9/_]).cpp:([0-9]):([0-9]): error: ", output_lines[line_num]):
    #         if (
    #             len(err_line_list) > 4
    #             and err_line_list[3] == " error"
    #             and err_line_list[1].isdecimal()
    #             and err_line_list[2].isdecimal()
    #         ):
    #             if error is not None:
    #                 error = error[:-1]
    #                 errors.append(error)
    #                 error = None
    #             if warning is not None:
    #                 warning = warning[:-1]
    #                 warnings.append(warning)
    #                 warning = None
    #
    #             err_amount += 1
    #             print(output_lines[line_num])
    #             error = [output_lines[line_num - 1]] if line_num > 0 else []
    #             error.append(output_lines[line_num])
    #         elif (
    #             len(err_line_list) > 4
    #             and err_line_list[3] == " warning"
    #             and err_line_list[1].isdecimal()
    #             and err_line_list[2].isdecimal()
    #         ):
    #             if error is not None:
    #                 error = error[:-1]
    #                 errors.append(error)
    #                 error = None
    #             if warning is not None:
    #                 warning = warning[:-1]
    #                 warnings.append(warning)
    #                 warning = None
    #             warn_amount += 1
    #             print(output_lines[line_num])
    #             warning = [output_lines[line_num - 1]] if line_num > 0 else []
    #             warning.append(output_lines[line_num])
    #         elif error is not None:
    #             error.append(output_lines[line_num])
    #         elif warning is not None:
    #             warning.append(output_lines[line_num])
    #
    #     print(f"{err_amount} errors , {warn_amount} warnings found")
    #     return errors, warnings
    #
    # def compile_make_target(self, target) -> int:
    #     try:
    #         subprocess.check_output(["make", target], stderr=subprocess.STDOUT)
    #     except subprocess.CalledProcessError as e:
    #         make_output: str = e.output.decode("utf-8")
    #         print("Compilation errors found:")
    #         # print(make_output)
    #         # erroneous_file = self.find_cpp_file(target)
    #         # print(f"Corresponding file: {erroneous_file}")
    #
    #         errors, warnings = self.parse_compilation_error(make_output)
    #
    #         for error in errors:
    #             props = error[1].split(":")
    #             filename = props[0]
    #             err_line: int = int(props[1])
    #             added_comment = f" // {err_line}"
    #             start_line, end_line, warnlines, filelines = self.read_lines(filename, err_line, 4, added_comment)
    #             print(error)
    #
    #             request = "Fix gcc compilation issue, write resulting code only:\n"
    #             for line in error:
    #                 request = request + line + "\n"
    #
    #             request = request + "Excerpt from the corresponding cpp file (not full):\n"
    #
    #             for line in warnlines:
    #                 request = request + line + "\n"
    #
    #             print("request")
    #             print(request)
    #             result: list[str]
    #             if self.debug:
    #                 result = [
    #                     "void print_usage(char* argv[])\n{\n"
    #                     + '  std::cout << "Usage: " << argv[0] << " filename.cpp" << std::endl;\n'
    #                     + '  return; // fix the error by removing "1"\n}\n\n'
    #                     + "int main(int argc, char* argv[])\n{"
    #                 ]
    #             else:
    #                 result = self.query_backend.query(request)
    #             print("result")
    #             print(result)
    #
    #             if len(result) > 0:
    #                 resulting_lines = self.prepare_lines(result[0], added_comment)
    #
    #                 self.diff_target.apply_diff(filename, start_line, end_line, resulting_lines, error[1])
    #
    #             if self.debug:
    #                 break
    #
    #     return 0

    def cpp_linking(self, params: dict | str):
        pass

    def cpp_tests(self, params: dict | str):
        pass
