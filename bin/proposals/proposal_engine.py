from __future__ import annotations

import copy
from typing import Final

from proposals.diff_proposal import DiffProposal

from abc import ABC, abstractmethod


class ProposalEngine(ABC):
    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self) -> DiffProposal:
        pass


class ProposalList(ProposalEngine):
    def __init__(self, proposals: list[DiffProposal]):
        self.proposals = proposals
        self.index = 0

    def __next__(self) -> DiffProposal:
        if self.index < len(self.proposals):
            prop = self.proposals[self.index]
            self.index += 1
            return prop
        else:
            raise StopIteration


class ProposalRepeat(ProposalEngine):
    def __init__(self, proposal: DiffProposal, times: int = 1):
        self.proposal: Final[DiffProposal] = proposal
        self.index: int = 0
        self.times: Final[int] = times

    def __next__(self) -> DiffProposal:
        if self.index < self.times:
            self.index += 1
            return self.proposal
        else:
            raise StopIteration


class ProposalEngineRepeat(ProposalEngine):
    def __init__(self, proposal_engine: ProposalEngine, times: int = 1):
        self.proposal_engine: Final[ProposalEngine] = proposal_engine
        self.index: int = 0
        self.times: Final[int] = times
        self.proposal_engine_current = copy.deepcopy(self.proposal_engine)

    def __next__(self) -> DiffProposal:
        try:
            return next(self.proposal_engine_current)
        except StopIteration:
            if self.index < self.times:
                self.index += 1
                self.proposal_engine_current = copy.deepcopy(self.proposal_engine)
                return next(self.proposal_engine_current)
            else:
                raise StopIteration


# class ProposalEngineList(ProposalEngine):
#     def __init__(self, proposal_engines : list[ProposalEngine]):
#         self.proposal_engines : Final[ProposalEngine] = proposal_engines
#         self.index : int = 0
#
#
#     def __next__(self) -> ProposalDiff:
#         try:
#             return next(self.proposal_engine_current)
#         except StopIteration:
#             if self.index < self.times:
#                 self.index += 1
#                 self.proposal_engine_current = copy.deepcopy(self.proposal_engine)
#                 return next(self.proposal_engine_current)
#             else:
#                 raise StopIteration
#
#
