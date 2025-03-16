# Copyright: Hallux team, 2023 - 2024

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

from ..proposals.proposal_engine import ProposalEngine
from .annotations import get_language


class IssueDescriptor(ABC):
    def __init__(
        self,
        tool: str,
        filename: str,
        issue_line: int = 0,
        description: str = "",
        issue_type: str = "warning",
        language: str | None = None,
        comment: str | None = None,
        line_comment: str | None = None,
    ):
        self.tool: Final[str] = tool
        self.filename: Final[str] = filename
        self.issue_line: int = issue_line
        self.description: str = description
        self.message_lines: list[str] = []
        self.issue_type: str = issue_type
        self.line_comment = line_comment

        if language is None or comment is None:
            language, comment = get_language(filename)
        self.language: Final[str] = language
        self.comment: Final[str] = comment

        if line_comment is None and comment is not None:
            # TODO: paarametrize line_comment template
            self.line_comment = f" {comment} <-- fix around this line {str(issue_line)}. Remove this comment after fix applied."

    @abstractmethod
    def list_proposals(self) -> ProposalEngine:
        # ToDo: we can provide QueryBackend or even a list[QueryBackend] in here
        # (or some kind of prioritized container)
        # This might give ability to try different Backends for different Proposals
        pass
