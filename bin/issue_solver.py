# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import ABC, abstractmethod
from issue import IssueDescriptor
from diff_target import DiffTarget
from query_backend import QueryBackend


# Base class for "proper" issue solving, i.e. issues solved one-by-one, with double-checking that fix was appropriate
# If fix wasn't successfull, we ignore it and go to the next issue
# For every tool such as 'ruff', or 'make compile', inherit separate class out of IssueSolver and define list_issues()
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
                print(f"{issue.filename}:{issue.issue_line}: {issue.description} : successfully fixed")
                # Do not touch issue_index
            else:
                diff_target.revert_diff()
                issue_index += 1
                target_issues = self.list_issues()
                print(f"{issue.filename}:{issue.issue_line}: {issue.description} : unable to fix")
