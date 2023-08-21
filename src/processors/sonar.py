# Copyright: Hallux team, 2023

from __future__ import annotations

import json
import os
from pathlib import Path

import requests

from backends.query_backend import QueryBackend
from issues.issue import IssueDescriptor
from issues.issue_solver import IssueSolver
from processors.code_processor import CodeProcessor
from proposals.diff_proposal import DiffProposal
from proposals.proposal_engine import ProposalEngine, ProposalList
from proposals.python_proposal import PythonProposal
from proposals.simple_proposal import SimpleProposal
from targets.diff_target import DiffTarget


class Sonar_IssueSolver(IssueSolver):
    def __init__(self, url: str, token: str, project: str = "hallux", success_test=None):
        super().__init__(success_test=success_test)
        self.url: str = url
        self.token: str = token
        self.project: str = project
        self.already_fixed_files = []

    def report_succesfull_fix(self, issue: IssueDescriptor, proposal: DiffProposal, query_backend: QueryBackend):
        self.already_fixed_files.append(issue.filename)
        super().report_succesfull_fix(issue, proposal, query_backend)

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []
        try:
            request: str = (
                self.url
                + "/api/issues/search?resolved=false&severities=MINOR,MAJOR,CRITICAL&statuses=OPEN,CONFIRMED,REOPENED"
            )
            if self.project is not None:
                request += "&componentKeys=" + self.project
            x = requests.get(url=request, headers={"Authorization": "Bearer " + self.token})
        except Exception:
            return []

        if x.status_code == 200:
            issues.extend(SonarIssue.parseIssues(x.text, self.already_fixed_files))

        return issues


class SonarIssue(IssueDescriptor):
    def __init__(
        self,
        filename: str,
        issue_line: int = 0,
        description: str = "",
        text_range: dict = dict,
        issue_type: str = "warning",
        already_fixed_files=None,
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
        self.already_fixed_files = already_fixed_files

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


class SonarProcessor(CodeProcessor):
    def __init__(
        self,
        query_backend: QueryBackend,
        diff_target: DiffTarget,
        run_path: Path,
        base_path: Path,
        config: dict,
        verbose: bool = False,
        sonarqube_token: str | None = None,
        sonarqube_url: str | None = None,
        sonarqube_project: str | None = None,
    ):
        super().__init__(query_backend, diff_target, run_path, base_path, config, verbose)

        self.token: str | None
        if sonarqube_token is not None:
            self.token = sonarqube_token
        elif "token" in config:
            self.token = config["token"]
        elif os.getenv("SONAR_TOKEN") is not None:
            self.token = os.getenv("SONAR_TOKEN")
        else:
            print("Cannot find SONAR_TOKEN")
            self.token = None

        self.url: str | None
        if sonarqube_url is not None:
            self.url = sonarqube_url
        elif "url" in config:
            self.url = config["url"]
        else:
            print("Cannot find SONAR URL")
            self.url = None

        self.sonarqube_project: str | None
        if sonarqube_project is not None:
            self.project = sonarqube_project
        elif "project" in config:
            self.project = config["project"]
        else:
            print("Cannot find SONAR PROJECT")
            self.project = None

    def process(self) -> None:
        if self.token is None or self.url is None:
            print("SONAR is not activated")
            return

        print("Process Sonarqube issues:")
        is_fix_succesful = self.is_fix_successful if self.success_test is not None else None
        issue_solver = Sonar_IssueSolver(self.url, self.token, self.project, success_test=is_fix_succesful)
        issue_solver.solve_issues(self.diff_target, self.query_backend)
