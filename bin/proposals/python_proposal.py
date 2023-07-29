# Copyright: Hallux team, 2023

from __future__ import annotations
import ast
import copy

from issues.issue import IssueDescriptor
from proposals.simple_proposal import SimpleProposal


class PythonProposal(SimpleProposal):
    def __init__(
        self,
        issue: IssueDescriptor,
        radius_or_range: int | tuple[int, int] = 4,  # radius or tuple with [start_line, end_line]
        issue_line_comment: str | None = None,
        extract_function: bool = False,
    ):
        super().__init__(issue, radius_or_range, issue_line_comment)
        if extract_function:
            with open(self.issue.filename, "rt") as f:
                python_source = f.read()
            # Parse the code into an AST
            parsed_ast = ast.parse(python_source, filename=self.issue.filename)

            # Find the target function
            target_function = None
            for node in ast.walk(parsed_ast):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    if node.lineno <= self.issue.issue_line <= node.end_lineno:
                        target_function = node
                        break

            if target_function:
                func_range = (target_function.lineno - 1, target_function.end_lineno)
                self._set_code_range(func_range)

        self.code_offset = 50000
        # count code offset
        for line in self.issue_lines:
            lsline = line.lstrip(" ")
            if len(lsline) > 0:  #
                self.code_offset = min(self.code_offset, len(line) - len(lsline))

        if self.code_offset > 0:
            for i, line in enumerate(self.issue_lines):
                self.issue_lines[i] = line[self.code_offset :]
            self.proposed_lines = copy.deepcopy(self.issue_lines)

    def _merge_lines(self, proposed_lines: list[str]) -> bool:
        if self.code_offset > 0:
            offset = " " * self.code_offset

            for i, line in enumerate(proposed_lines):
                proposed_lines[i] = offset + line

            for i, line in enumerate(self.issue_lines):
                self.issue_lines[i] = offset + line

        return super()._merge_lines(proposed_lines)
