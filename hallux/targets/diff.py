# Copyright: Hallux team, 2023

# We have several options where (and how) to send found fixes (aka FileDiff).
# 1. FilesystemTarget (most primitive one) - it simply to re-write local files
# 2. GitCommitTarget (little more complicated) - rewrite local files, but also make git commit on every change
# 3. GithubProposalTarget - submit all changes into Github Web Interface as proposals/suggestions
#    This last one requires some extra configuring to be done
# All those approaches are hidden after DiffTarget interface written in this file

from __future__ import annotations

from abc import ABC, abstractmethod

from ..proposals.diff_proposal import DiffProposal


# Interface for DiffTarget implementations
# It has some kind of state:
# * DiffProposal needs to be firstly applied (temporally),
# * then checked/tested by some other means,
# * if check was successful DiffProposal shall be finally committed
# * otherwise reverted
class DiffTarget(ABC):
    @abstractmethod
    def apply_diff(self, diff: DiffProposal) -> bool:
        pass

    @abstractmethod
    def revert_diff(self) -> None:
        pass

    @abstractmethod
    def commit_diff(self) -> bool:
        pass

    @abstractmethod
    def requires_refresh(self) -> bool:
        """
        :return: true if issues need to be refreshed, after successful solve.
                 Could be due-to line-numbers change, or other reasons.
        """
        pass
