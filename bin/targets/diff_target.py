# Copyright: Hallux team, 2023

# We have several options where (and how) to send found fixes (aka FileDiff).
# 1. FilesystemTarget (most primitive one) - it simply to re-write local files
# 2. GitCommitTarget (little more complicated) - rewrite local files, but also make git commit on every change
# 3. GithubProposalTarget - submit all changes into Github Web Interface as proposals/suggestions
#    This last one requires some extra configuring to be done
# All those approaches are hidden after DiffTarget interface written in this file

from __future__ import annotations
from abc import ABC, abstractmethod
from file_diff import FileDiff


# Interface for DiffTarget implementations
# It has some kind of state, where FileDiff needs to be firstly applied,
# then checked/tested (by some other means),
# and if check was successful diff shall be finally committed
# or reverted, if check fails
class DiffTarget(ABC):
    @abstractmethod
    def apply_diff(self, diff: FileDiff) -> bool:
        pass

    @abstractmethod
    def revert_diff(self) -> None:
        pass

    @abstractmethod
    def commit_diff(self) -> bool:
        """
        :return: true if issues are solved independently
                (i.e. need to increment issue_index in the IssueSolver)
        """
        pass
