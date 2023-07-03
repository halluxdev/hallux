# Copyright: Hallux team, 2023

from __future__ import annotations

from code_processor import set_directory
from file_diff import FileDiff
from query_backend import QueryBackend
from targets.diff_target import DiffTarget
from issue_solver import IssueSolver
from issue import IssueDescriptor
from pathlib import Path
import subprocess


class MakeCompile_IssueSolver(IssueSolver):
    def __init__(self, make_target: str, base_path: Path, makefile_dir: Path):
        self.make_target = make_target
        self.base_path = base_path
        self.makefile_dir = makefile_dir

    def solve_issues(self, diff_target: DiffTarget, query_backend: QueryBackend):
        with set_directory(self.base_path):
            super().solve_issues(diff_target, query_backend)

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []

        with set_directory(self.makefile_dir):
            try:
                subprocess.check_output(["make", self.make_target], stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                make_output: str = e.output.decode("utf-8")
                issues.extend(CppIssueDescriptor.parseMakeIssues(make_output))

        return issues


class CppIssueDescriptor(IssueDescriptor):
    def __init__(self, filename: str, issue_line: int = 0, description: str = ""):
        super().__init__(
            language="cpp", tool="compile", filename=filename, issue_line=issue_line, description=description
        )

    def try_fixing(self, query_backend: QueryBackend, diff_target: DiffTarget):
        line_comment: str = f" // line {str(self.issue_line)}"
        diff: FileDiff = FileDiff(
            self.filename, self.issue_line, radius=4, issue_line_comment=line_comment, description=self.description
        )
        request_lines = [
            "Fix gcc compilation issue:",
            *self.message_lines,
            "from corresponding c++ code:\n```",
            *diff.issue_lines,
            "```\nWrite back fixed code ONLY:\n",
        ]
        request = "\n".join(request_lines)
        result: list[str] = query_backend.query(request, self)

        if len(result) > 0:
            diff.propose_lines(result[0])
            diff_target.apply_diff(diff)

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
