# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import ABC, abstractmethod

from issues.issue import IssueDescriptor
from proposals.diff_proposal import DiffProposal
from targets.diff_target import DiffTarget
from backends.query_backend import QueryBackend


# Base class for "proper" issue solving, i.e. issues solved one-by-one, with double-checking that fix was appropriate
# If fix wasn't successfull, we ignore it and go to the next issue
# For every tool such as 'ruff', or 'make compile', inherit separate class out of IssueSolver and define list_issues()
class IssueSolver(ABC):
    def __init__(self, success_test=None):
        self.success_test = success_test

    @abstractmethod
    def list_issues(self) -> list[IssueDescriptor]:
        pass

    def is_issue_fixed(self, target_issues: list[IssueDescriptor]) -> bool:
        if self.success_test is not None:
            return self.success_test()
        else:
            new_issues = self.list_issues()
            # Number of issues decreased => FIX SUCCESFULL
            return len(new_issues) < len(target_issues)

    def report_succesfull_fix(self, issue: IssueDescriptor, proposal: DiffProposal, query_backend: QueryBackend):
        query_backend.report_succesfull_fix(issue, proposal)

    def solve_issues(self, diff_target: DiffTarget, query_backend: QueryBackend):
        issue_index: int = 0
        target_issues = self.list_issues()
        while issue_index < len(target_issues):
            issue = target_issues[issue_index]

            proposals = issue.list_proposals()
            fixing_successful: bool = False
            print(f"{issue.filename}:{issue.issue_line}: {issue.description} : ", end="")

            proposal: DiffProposal | None = None
            for proposal in proposals:
                applying_successful: bool
                used_backend = None

                iters = 10
                while used_backend != query_backend and iters > 0:
                    iters -= 1
                    try:
                        applying_successful, used_backend = proposal.try_fixing_with_priority(
                            diff_target=diff_target, query_backend=query_backend, used_backend=used_backend
                        )
                    except Exception as e:
                        diff_target.revert_diff()
                        raise e

                    if applying_successful:
                        fixing_successful = self.is_issue_fixed(target_issues)
                    else:
                        diff_target.revert_diff()
                        continue

                    if fixing_successful:
                        # this is a good place for "multi-step proposal" extension
                        fixing_successful = diff_target.commit_diff()
                        # commit_diff() might not be OK
                        if fixing_successful:
                            break

                if fixing_successful:
                    break

                diff_target.revert_diff()

            if fixing_successful:
                # provide feedback, in order to collect training data
                self.report_succesfull_fix(issue, proposal, query_backend)
                if diff_target.requires_refresh():
                    target_issues = self.list_issues()
                else:
                    issue_index += 1
                print(" \033[92m successfully fixed\033[0m")
            else:
                issue_index += 1
                print(" \033[91m unable to fix\033[0m")
