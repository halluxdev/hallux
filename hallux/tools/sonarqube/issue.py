# Copyright: Hallux team, 2023 - 2024

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
            proposal_list = [
                PythonProposal(self, extract_function=True),
                PythonProposal(self, radius_or_range=10),
            ]
            if end_line - start_line > 4:
                proposal_list.append(PythonProposal(self, radius_or_range=code_range))

        else:
            proposal_list = [
                SimpleProposal(self, radius_or_range=10),
                SimpleProposal(self, radius_or_range=100),
            ]
            if end_line - start_line > 4:
                proposal_list.append(SimpleProposal(self, radius_or_range=code_range))

        return ProposalList(proposal_list)

    @staticmethod
    def parseIssues(request_output: str, already_fixed_files: list[str] | None = None) -> list[SonarIssue]:
        js = json.loads(request_output)

        issues: list[SonarIssue] = []
        for json_issue in js["issues"]:
            comp_arr = json_issue["component"].split(":")
            # TODO: do we need any extra-filter here?
            # if comp_arr != self.project:
            #     continue
            filename = comp_arr[-1]

            if "line" not in json_issue:
                logger.message(
                    f"{filename}: {json_issue['message']}  \033[91m unable to fix\033[0m"
                )
                continue

            issue = SonarIssue(
                filename=filename,
                issue_line=json_issue["line"],
                description=json_issue["message"],
                text_range=json_issue["textRange"],
                issue_type=str(json_issue["type"]).replace("_", " "),
                already_fixed_files=already_fixed_files,
            )

            issues.append(issue)

        return issues
