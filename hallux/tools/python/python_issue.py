# Copyright: Hallux team, 2023

from __future__ import annotations

from ...issues.issue import IssueDescriptor
from ...proposals.proposal_engine import ProposalEngine, ProposalList
from ...proposals.python_proposal import PythonProposal


class PythonIssue(IssueDescriptor):
    def __init__(self, filename: str, issue_line: int = 0, description: str = "", tool: str = "ruff"):
        super().__init__(
            language="python", tool=tool, filename=filename, issue_line=issue_line, description=description
        )

    def list_proposals(self) -> ProposalEngine:
        line_comment: str = f" # line {str(self.issue_line)}"
        return ProposalList(
            [
                PythonProposal(self, extract_function=True, issue_line_comment=line_comment),
                PythonProposal(self, radius_or_range=4, issue_line_comment=line_comment),
                PythonProposal(self, radius_or_range=6, issue_line_comment=line_comment),
            ]
        )

    @staticmethod
    def parseIssues(ruff_output: str, tool: str = "ruff", keyword: str = "") -> list[PythonIssue]:
        issues: list[PythonIssue] = []
        warnings: list[str] = ruff_output.split("\n")
        for warn in warnings[:-2]:
            warn_arr = warn.split(" ")
            if len(warn_arr) < 3:
                break
            filename_line_col = warn_arr[0].split(":")
            if len(filename_line_col) < 3:
                break
            filename = filename_line_col[0]
            issue_line = int(filename_line_col[1])

            if len(keyword) == 0 or str(warn_arr[1:]).startswith(keyword):
                issue = PythonIssue(
                    filename=filename,
                    issue_line=issue_line,
                    description=str(" ".join(warn_arr[1:]).lstrip(" ")),
                    tool=tool,
                )
                issues.append(issue)

        return issues
