# Copyright: Hallux team, 2023

from __future__ import annotations

import ast
import copy

from ..issues.issue import IssueDescriptor
from .simple_proposal import SimpleProposal


class PythonProposal(SimpleProposal):
    def __init__(
        self,
        issue: IssueDescriptor,
        # radius or tuple with [start_line, end_line]
        radius_or_range: int | tuple[int, int] = 4,
        issue_line_comment: str | None = None,
        extract_function: bool = False,
    ):
        super().__init__(issue, radius_or_range, issue_line_comment)
        if extract_function:
            self.extract_function(issue)
        self.code_offset = 50000
        self.count_code_offset()
        if self.code_offset > 0:
            self.remove_code_offset()

    def extract_function(self, issue):
        with open(issue.filename, "rt") as f:
            python_source = f.read()
        parsed_ast = ast.parse(python_source, filename=issue.filename)
        target_function = self.find_target_function(parsed_ast, issue.issue_line)
        if target_function:
            func_range = (target_function.lineno, target_function.end_lineno)
            self._set_code_range(func_range)

    def find_target_function(self, parsed_ast, issue_line):
        for node in ast.walk(parsed_ast):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.lineno <= issue_line <= node.end_lineno:
                    return node

    def count_code_offset(self):
        for line in self.issue_lines:
            lsline = line.lstrip(" ")
            if len(lsline) > 0:
                self.code_offset = min(self.code_offset, len(line) - len(lsline))

    def remove_code_offset(self):
        for i, line in enumerate(self.issue_lines):
            self.issue_lines[i] = line[self.code_offset :]
        self.proposed_lines = copy.deepcopy(self.issue_lines)

    def _merge_lines(self, proposed_lines: list[str]) -> bool:
        if self.code_offset > 0:
            offset = " " * self.code_offset

            for i, line in enumerate(proposed_lines):
                if len(line) > 0:
                    proposed_lines[i] = offset + line

            for i, line in enumerate(self.issue_lines):
                if len(line) > 0:
                    self.issue_lines[i] = offset + line

        return super()._merge_lines(proposed_lines)
