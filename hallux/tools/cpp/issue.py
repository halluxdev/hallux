# Copyright: Hallux team, 2023 - 2024

from __future__ import annotations

from pathlib import Path

from ...issues.issue import IssueDescriptor
from ...proposals.proposal_engine import ProposalEngine, ProposalList
from ...proposals.simple_proposal import SimpleProposal


class CppIssue(IssueDescriptor):
    def __init__(self, filename: str, issue_line: int = 0, description: str = ""):
        super().__init__(
            language="cpp", tool="compile", filename=filename, issue_line=issue_line, description=description
        )
        self.issue_type = "compilation"

    def list_proposals(self) -> ProposalEngine:
        return ProposalList(
            [
                SimpleProposal(self, radius_or_range=3),
                SimpleProposal(self, radius_or_range=4),
                SimpleProposal(self, radius_or_range=5),
                SimpleProposal(self, radius_or_range=6),
            ]
        )

    @staticmethod
    def parseMakeIssues(make_output: str, debug: bool = False) -> list[CppIssue]:
        issues: list[CppIssue] = []
        output_lines: list[str] = make_output.split("\n")
        current_issue: CppIssue | None = None

        for line_num in range(len(output_lines)):
            err_line_list = output_lines[line_num].split(":")
            if (
                len(err_line_list) > 4
                and Path(err_line_list[0]).exists()
                and err_line_list[1].isdecimal()
                and err_line_list[2].isdecimal()
                and (err_line_list[3] == " error" or err_line_list[3] == " warning")
            ):
                if current_issue is not None:
                    current_issue.message_lines = current_issue.message_lines[:-1]
                    issues.append(current_issue)

                current_issue = CppIssue(
                    filename=err_line_list[0],
                    issue_line=int(err_line_list[1]),
                    description=str(":".join(err_line_list[4:]).lstrip(" ")),
                )
                current_issue.message_lines = [output_lines[line_num]]
                current_issue.debug = debug

            elif current_issue is not None:
                if output_lines[line_num].startswith("make"):
                    issues.append(current_issue)
                    current_issue = None
                else:
                    current_issue.message_lines.append(output_lines[line_num])

        if current_issue is not None:
            issues.append(current_issue)

        return issues
