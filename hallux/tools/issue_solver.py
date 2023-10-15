# Copyright: Hallux team, 2023

from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Final

from hallux.logger import logger

from ..auxilary import set_directory
from ..backends.query_backend import QueryBackend
from ..issues.issue import IssueDescriptor
from ..proposals.diff_proposal import DiffProposal
from ..targets.diff import DiffTarget


class IssueSolver(ABC):
    """
    Base abstract class for issue solving.
    For every tool such as 'ruff', or 'make', one need to inherit a class out and define list_issues()
    Issues repeatedly solved one-by-one, with check that fix was appropriate (is_issue_fixed func is used).
    If fix wasn't successful, we ignore issue (and revert corresponding fix) and go to the next one.
    """

    def __init__(
        self,
        config_path: Path,
        run_path: Path,
        command_dir: str = ".",
        validity_test: str | None = None,
    ):
        self.config_path: Final[Path] = config_path
        self.run_path: Final[Path] = run_path
        self.command_dir: Final[str] = command_dir
        self.validity_test: Final[str] = validity_test

        if validity_test is not None:
            try:
                logger.info(f"Try running validity test: {validity_test} ...")

                with set_directory(self.config_path):
                    subprocess.check_output(
                        ["bash"] + validity_test.split(" "),
                    )
                    logger.info("\033[92m PASSED\033[0m")
            except subprocess.CalledProcessError as e:
                raise SystemError(f"Validity Test '{validity_test}' is failing right from the start") from e

    @abstractmethod
    def list_issues(self) -> list[IssueDescriptor]:
        """
        Shall be implemented in child class
        :return: List of issued for a particular Processor/Solver
        """
        pass

    def is_issue_fixed(self) -> bool:
        """
        :returns: True, if latest fix was successful
        """
        if self.validity_test is not None:
            try:
                with set_directory(self.config_path):
                    subprocess.check_output(["bash"] + self.validity_test.split(" "))
                logger.info(f"validity test: {self.validity_test} PASSED")
                return True
            except subprocess.CalledProcessError:
                logger.info(f"\033[91m validity test: {self.validity_test} FAILED\033[0m")
                return False
        else:
            new_issues = self.list_issues()
            # Number of issues decreased => FIX SUCCESFULL
            return len(new_issues) < len(self.target_issues)

    def solve_issues(self, diff_target: DiffTarget, query_backend: QueryBackend):
        issue_index: int = 0
        self.target_issues = self.list_issues()
        while issue_index < len(self.target_issues):
            issue = self.target_issues[issue_index]

            proposals = issue.list_proposals()
            fixing_successful: bool = False

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
                        fixing_successful = self.is_issue_fixed()
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

                # if whole loop passed, but there were no successful fix, revert the change
                diff_target.revert_diff()

            if fixing_successful:
                # provide feedback, in order to collect training data
                query_backend.report_succesfull_fix(issue, proposal)
                if diff_target.requires_refresh():
                    self.target_issues = self.list_issues()
                else:
                    issue_index += 1
                logger.message(
                    f"{issue.filename}:{issue.issue_line}: {issue.description}  \033[92m successfully fixed\033[0m"
                )
            else:
                issue_index += 1
                logger.message(
                    f"{issue.filename}:{issue.issue_line}: {issue.description}  \033[91m unable to fix\033[0m"
                )
