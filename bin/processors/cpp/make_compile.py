# Copyright: Hallux team, 2023

from __future__ import annotations

import subprocess
from pathlib import Path

from auxilary import set_directory
from backends.query_backend import QueryBackend
from issues.issue import IssueDescriptor
from issues.issue_solver import IssueSolver
from proposals.proposal_engine import ProposalEngine, ProposalList
from proposals.simple_proposal import SimpleProposal
from targets.diff_target import DiffTarget


class MakeCompile_IssueSolver(IssueSolver):
    def __init__(self, make_target: str, makefile_dir: Path, verbose: bool = False):
        super().__init__()
        self.make_target = make_target
        self.base_path = makefile_dir
        self.verbose = verbose

    def solve_issues(self, diff_target: DiffTarget, query_backend: QueryBackend):
        if self.verbose:
            print(f"{self.base_path}/Makefile : '{self.make_target}'")
        with set_directory(self.base_path):
            super().solve_issues(diff_target, query_backend)

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []

        with set_directory(self.base_path):
            try:
                subprocess.check_output(["make", self.make_target], stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                make_output: str = e.output.decode("utf-8")
                issues.extend(CppIssueDescriptor.parseMakeIssues(make_output))

        return issues


class CppIssueDescriptor(IssueDescriptor):
    def __init__(self, filename: str, issue_line: int = 0, description: str = ""):
        super().__init__(
            language="cpp", tool="compile", filename=filename, issue_line=issue_line, description=description
        )
        self.issue_type = "compilation"

    def list_proposals(self) -> ProposalEngine:
        line_comment: str = f" // line {str(self.issue_line)}"
        return ProposalList(
            [
                SimpleProposal(self, radius_or_range=3, issue_line_comment=line_comment),
                SimpleProposal(self, radius_or_range=4, issue_line_comment=line_comment),
                SimpleProposal(self, radius_or_range=5, issue_line_comment=line_comment),
                SimpleProposal(self, radius_or_range=6, issue_line_comment=line_comment),
            ]
        )

    @staticmethod
    def parseMakeIssues(make_output: str, debug: bool = False) -> list[CppIssueDescriptor]:
        issues: list[CppIssueDescriptor] = []
        output_lines: list[str] = make_output.split("\n")
        current_issue: CppIssueDescriptor | None = None

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

                current_issue = CppIssueDescriptor(
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
