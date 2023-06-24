#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import ABC, abstractmethod
import copy
from issue import IssueDescriptor
from diff_target import DiffTarget
from query_backend import QueryBackend


class IssueSolver(ABC):
    @abstractmethod
    def list_issues(self) -> list[IssueDescriptor]:
        pass

    def solve_issues(self, diff_target: DiffTarget, query_backend: QueryBackend):
        issue_index: int = 0
        target_issues = self.list_issues()
        while issue_index < len(target_issues):
            issue = target_issues[issue_index]
            issue.try_fixing(diff_target=diff_target, query_backend=query_backend)
            new_target_issues: list[IssueDescriptor] = self.list_issues()

            if len(new_target_issues) < len(target_issues):
                # Number of issues decreased => FIX SUCCESFULL
                diff_target.commit_diff()
                target_issues = new_target_issues
                print(f"{issue.filename}:{issue.issue_line}: {issue.description} : SUCCESSFULLY FIXED")
                # Do not touch issue_index
            else:
                diff_target.revert_diff()
                issue_index += 1
                target_issues = self.list_issues()
                print(f"{issue.filename}:{issue.issue_line}: {issue.description} : unable to fix")


class CodeProcessor:
    @staticmethod
    def read_lines(
        filename: str, line: int, raidus: int, add_comment: str | None = None
    ) -> tuple[int, int, list[str], list[str]]:
        with open(filename, "rt") as file:
            filelines = file.read().split("\n")
        start_line = max(0, line - raidus)
        end_line = min(len(filelines) - 1, line + raidus)
        requested_lines = copy.deepcopy(filelines[start_line:end_line])
        requested_lines[line - start_line] += add_comment
        return start_line, end_line, requested_lines, filelines

    @staticmethod
    def prepare_lines(query_result: str, remove_comment: str | None = None) -> list[str]:
        resulting_lines = query_result.split("\n")
        for i in range(len(resulting_lines)):
            line: str = resulting_lines[i]
            if line.endswith(remove_comment):
                resulting_lines[i] = line[: -len(remove_comment)]
                break
        return resulting_lines
