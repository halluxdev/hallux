# Copyright: Hallux team, 2023

from __future__ import annotations

import json
from typing import Final

from ...issues.issue import IssueDescriptor
from ...proposals.proposal_engine import ProposalEngine, ProposalList
from ...proposals.python_proposal import PythonProposal
from ...proposals.simple_proposal import SimpleProposal


class SonarIssue(IssueDescriptor):
    def __init__(
        self,
        filename: str,
        issue_line: int = 0,
        description: str = "",
        text_range: dict = dict,
        issue_type: str = "warning",
        already_fixed_files: list[str] | None = None,
    ):
        super().__init__(
            language=None,
            tool="sonar",
            filename=filename,
            issue_line=issue_line,
            description=description,
            issue_type=issue_type,
        )
        if already_fixed_files is None:
            already_fixed_files = list()
        self.text_range: dict = text_range
        self.already_fixed_files: Final[list[str]] = already_fixed_files

    def list_proposals(self) -> ProposalEngine:
        start_line: int = self.text_range["startLine"]
        end_line: int = self.text_range["endLine"]
        code_range = (start_line, end_line)

        # we may only fix 1 issue per file for SonarQube
        if self.filename in self.already_fixed_files:
            return ProposalList([])

        if self.language == "python":
            line_comment: str = f" # line {str(self.issue_line)}"
            proposal_list = [
                PythonProposal(self, extract_function=True, issue_line_comment=line_comment),
                PythonProposal(self, radius_or_range=4, issue_line_comment=line_comment),
            ]
            if end_line - start_line > 4:
                proposal_list.append(PythonProposal(self, radius_or_range=code_range, issue_line_comment=line_comment))

        else:
            proposal_list = [
                SimpleProposal(self, radius_or_range=4),
                SimpleProposal(self, radius_or_range=6),
            ]
            if end_line - start_line > 4:
                proposal_list.append(SimpleProposal(self, radius_or_range=code_range))

        return ProposalList(proposal_list)

    @staticmethod
    def parseIssues(request_output: str, already_fixed_files: list[str] | None = None) -> list[SonarIssue]:
        js = json.loads(request_output)

        issues: list[SonarIssue] = []
        for js_issue in js["issues"]:
            comp_arr = js_issue["component"].split(":")
            # ToDo: do we need any extra-filter here?
            # if comp_arr != self.project:
            #     continue
            filename = ":".join(comp_arr[1:])

            issue = SonarIssue(
                filename=filename,
                issue_line=js_issue["line"],
                description=js_issue["message"],
                text_range=js_issue["textRange"],
                issue_type=str(js_issue["type"]).replace("_", " "),
                already_fixed_files=already_fixed_files,
            )

            issues.append(issue)

        return issues
