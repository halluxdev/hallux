# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import ABC, abstractmethod

from issues.issue import IssueDescriptor
from proposals.diff_proposal import DiffProposal
from targets.diff_target import DiffTarget
from backend.query_backend import QueryBackend


# Base class for "proper" issue solving, i.e. issues solved one-by-one, with double-checking that fix was appropriate
# If fix wasn't successfull, we ignore it and go to the next issue
# For every tool such as 'ruff', or 'make compile', inherit separate class out of IssueSolver and define list_issues()
class IssueSolver(ABC):
    @abstractmethod
    def list_issues(self) -> list[IssueDescriptor]:
        pass

    def is_issue_fixed(self, target_issues: list[IssueDescriptor]) -> bool:
        new_issues = self.list_issues()
        # Number of issues decreased => FIX SUCCESFULL
        return len(new_issues) < len(target_issues)

    def solve_issues(self, diff_target: DiffTarget, query_backend: QueryBackend):
        issue_index: int = 0
        target_issues = self.list_issues()
        while issue_index < len(target_issues):
            issue = target_issues[issue_index]

            proposals = issue.list_proposals()
            fixing_successful: bool = False

            proposal: DiffProposal
            for proposal in proposals:
                applying_successful: bool
                try:
                    applying_successful = proposal.try_fixing(diff_target=diff_target, query_backend=query_backend)
                except Exception as e:
                    diff_target.revert_diff()
                    raise e

                if applying_successful:
                    fixing_successful = self.is_issue_fixed(target_issues)
                else:
                    diff_target.revert_diff()
                    continue

                if fixing_successful:
                    # ToDo: here we may provide feedback to proposal, in order to collect training data
                    # Also, this is a good place for "multi-step proposal" extension
                    break

            if fixing_successful:
                diff_target.commit_diff()
                if diff_target.requires_refresh():
                    target_issues = self.list_issues()
                else:
                    issue_index += 1
                print(f"{issue.filename}:{issue.issue_line}: {issue.description} : successfully fixed")
            else:
                diff_target.revert_diff()
                issue_index += 1
                print(f"{issue.filename}:{issue.issue_line}: {issue.description} : unable to fix")
                continue
