# Copyright: Hallux team, 2023

from __future__ import annotations

from backend.query_backend import QueryBackend
from proposals.proposal_engine import ProposalEngine, ProposalList
from proposals.simple_proposal import SimpleProposal
from targets.diff_target import DiffTarget
from code_processor import CodeProcessor
import requests
import os
from pathlib import Path
from proposals.diff_proposal import DiffProposal
from issues.issue import IssueDescriptor
from issues.issue_solver import IssueSolver
import json


class Sonar_IssueSolver(IssueSolver):
    def __init__(self, url: str, token: str, project: str = "hallux"):
        self.url: str = url
        self.token: str = token
        self.project: str = project

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []
        try:
            request: str = (
                self.url
                + "/api/issues/search?resolved=false&severities=MINOR,MAJOR,CRITICAL&statuses=OPEN,CONFIRMED,REOPENED"
            )
            if self.project is not None:
                request += "&componentKeys=hallux"
            x = requests.get(url=request, headers={"Authorization": "Bearer " + self.token})
        except Exception:
            return []

        if x.status_code == 200:
            issues.extend(SonarIssue.parseIssues(x.text))

        return issues


class SonarIssue(IssueDescriptor):
    def __init__(
        self,
        filename: str,
        issue_line: int = 0,
        description: str = "",
        text_range: dict = dict,
        issue_type: str = "warning",
    ):
        super().__init__(
            language=None,
            tool="sonar",
            filename=filename,
            issue_line=issue_line,
            description=description,
            issue_type=issue_type,
        )
        self.text_range: dict = text_range

    def list_proposals(self) -> ProposalEngine:
        line_comment: str = f" # line {str(self.issue_line)}"
        start_line: int = self.text_range["startLine"] - self.text_range["startOffset"]
        end_line: int = self.text_range["endLine"] + self.text_range["endOffset"]
        code_range = (start_line, end_line)

        return ProposalList([SimpleProposal(self, radius_or_range=code_range, issue_line_comment=line_comment)])

    def try_fixing(self, query_backend: QueryBackend, diff_target: DiffTarget) -> bool:
        line_comment: str = f" # line {str(self.issue_line)}"
        start_line: int = self.text_range["startLine"] - self.text_range["startOffset"]
        end_line: int = self.text_range["endLine"] + self.text_range["endOffset"]
        code_range = (start_line, end_line)
        self.file_diff = DiffProposal(
            self.filename,
            self.issue_line,
            radius_or_range=code_range,
            description=self.description,
            issue_line_comment=line_comment,
        )
        request_lines = [
            "Fix " + self.issue_type + " issue: " + self.description,
            "from corresponding " + self.language + " code:\n```",
            *self.file_diff.issue_lines,
            "```\nWrite back ONLY fixed code, keep formatting:",
        ]
        request = "\n".join(request_lines)
        result: list[str] = query_backend.query(request, self)

        if len(result) > 0:
            self.file_diff.propose_lines(result[0])
            return diff_target.apply_diff(self.file_diff)

        return False

    @staticmethod
    def parseIssues(request_output: str) -> list[SonarIssue]:
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
            )

            issues.append(issue)

        return issues


class SonarProcessor(CodeProcessor):
    def __init__(
        self,
        query_backend: QueryBackend,
        diff_target: DiffTarget,
        base_path: Path,
        config: dict,
        verbose: bool = False,
        sonarqube_token: str | None = None,
        sonarqube_url: str | None = None,
    ):
        super().__init__(query_backend, diff_target, config, verbose)
        self.base_path: Path = base_path

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

    def process(self) -> None:
        if self.token is None or self.url is None:
            print("SONAR is not activated")
            return

        print("Process Sonarqube issues:")
        issue_solver = Sonar_IssueSolver(self.url, self.token)
        issue_solver.solve_issues(self.diff_target, self.query_backend)
