# Copyright: Hallux team, 2023

from __future__ import annotations

from file_diff import FileDiff
from backend.query_backend import QueryBackend
from targets.diff_target import DiffTarget
from issue import IssueDescriptor
from issue_solver import IssueSolver
import subprocess


class Ruff_IssueSolver(IssueSolver):
    def __init__(self, ruff_dir: str | None = None):
        self.ruff_dir: str = ruff_dir if ruff_dir is not None else "."

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []
        try:
            ruff_output = subprocess.check_output(["ruff", "check", self.ruff_dir])
        except subprocess.CalledProcessError as e:
            ruff_output = e.output

        issues.extend(RuffIssue.parseRuffIssues(ruff_output.decode("utf-8")))

        return issues


class RuffIssue(IssueDescriptor):
    def __init__(self, filename: str, issue_line: int = 0, description: str = ""):
        super().__init__(
            language="python", tool="ruff", filename=filename, issue_line=issue_line, description=description
        )

    def try_fixing(self, query_backend: QueryBackend, diff_target: DiffTarget):
        line_comment: str = f" # line {str(self.issue_line)}"
        self.file_diff = FileDiff(
            self.filename, self.issue_line, radius=5, description=self.description, issue_line_comment=line_comment
        )
        request_lines = [
            "Fix python linting issue: " + self.description,
            "from corresponding python code:\n```",
            *self.file_diff.issue_lines,
            "```\nWrite back ONLY fixed code, keep formatting:\n",
        ]
        request = "\n".join(request_lines)
        result: list[str] = query_backend.query(request, self)

        if len(result) > 0:
            self.file_diff.propose_lines(result[0])
            diff_target.apply_diff(self.file_diff)

    @staticmethod
    def parseRuffIssues(ruff_output: str) -> list[RuffIssue]:
        issues: list[RuffIssue] = []
        warnings: list[str] = ruff_output.split("\n")
        for warn in warnings[:-2]:
            warn_arr = warn.split(" ")
            if len(warn_arr) < 3:
                break
            filename_line_col = warn_arr[0].split(":")
            if len(filename_line_col) < 3:
                break
            filename = filename_line_col[0]
            issue_line = int(filename_line_col[1])

            issue = RuffIssue(
                filename=filename,
                issue_line=issue_line,
                description=str(" ".join(warn_arr[1:]).lstrip(" ")),
            )
            issues.append(issue)

        return issues
