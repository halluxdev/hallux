# Copyright: Hallux team, 2023-2024

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Final

import requests

from hallux.logger import logger

from ...backends.query_backend import QueryBackend
from ...targets.diff import DiffTarget
from ..issue_solver import IssueSolver
from .issue import IssueDescriptor, SonarIssue


class OverrideQueryBackend(QueryBackend):
    """
    With SonarQube we only may solve 1 issue per file.
    We override QueryBackend to track files with successful fixes.
    Later, this file list is used to avoid any other fixes
    """

    def __init__(self, underlying_backend: QueryBackend, already_fixed_files: list[str]):
        super().__init__()
        self.backend: Final[QueryBackend] = underlying_backend
        self.already_fixed_files: Final[list[str]] = already_fixed_files

    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:
        return self.backend.query(request, issue, issue_lines)

    def report_successful_fix(self, issue, proposal) -> None:
        self.already_fixed_files.append(issue.filename)
        self.backend.report_successful_fix(issue, proposal)


class Sonar_IssueSolver(IssueSolver):
    SONAR_TOKEN: Final[str] = "SONAR_TOKEN"

    def __init__(
        self,
        config_path: Path,
        run_path: Path,
        command_dir: str = ".",
        validity_test: str | None = None,
        url: str | None = None,
        token: str | None = None,
        project: str | None = None,
        search_params: str = "resolved=false&severities=MINOR,MAJOR,CRITICAL&statuses=OPEN,CONFIRMED,REOPENED",
        argvalue: str | None = None,  # example: "branch=65-sonar-fixes"
    ):
        """
        IssueSolver implementation for SonarQube
        :param config_path: Directory with .hallux file
        :param run_path: Directory, where hallux was run
        :param command_dir: Directory, passed to hallux in CLI
        :param validity_test: script
        :param url:
        :param token:
        :param project:
        :param search_params:
        :param argvalue: It could be a path to a .json file, or a string with extra params
        """
        super().__init__(config_path, run_path, command_dir, validity_test=validity_test)

        self.token: Final[str | None] = token if token is not None else os.getenv(self.SONAR_TOKEN)
        self.url: Final[str | None] = url
        self.project: Final[str | None] = project
        self.search_params: Final[str] = search_params
        self.argvalue: Final[str | None] = argvalue

        # With SonarQube we only may solve 1 issue per file.
        self.already_fixed_files: Final[list[str]] = []

    def solve_issues(self, diff_target: DiffTarget, query_backend: QueryBackend):
        if not self._check_file() and (not self.token or not self.url or not self.project):
            logger.error("SonarQube: token, url or project not configured")
            return

        logger.message("Process SonarQube issues:")
        new_query_backend = OverrideQueryBackend(query_backend, self.already_fixed_files)
        super().solve_issues(diff_target, new_query_backend)

    def _check_file(self):
        return self.argvalue and self.argvalue.endswith(".json") and Path(self.argvalue).exists()

    def is_issue_fixed(self) -> bool:
        if self.validity_test is None:
            return True
        else:
            return super().is_issue_fixed()

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []

        # ToDo: make some caching for issues, in order not to query sonar every time
        response_json: str
        if self._check_file():
            logger.info("SONAR extra_params is a json file: " + self.argvalue)
            with open(self.argvalue, "r") as f:
                response_json = f.read()
        else:
            try:
                request: str = self.url + "/api/issues/search?" + self.search_params
                if self.argvalue is not None:
                    request += "&" + self.argvalue
                if self.project is not None:
                    request += "&componentKeys=" + self.project
                logger.debug("Sonar URL: " + request)
                x = requests.get(url=request, headers={"Authorization": "Bearer " + self.token})
            except Exception:
                return []

            if x.status_code == 200:
                response_json = x.text
            else:
                logger.error(f'SonarQube: error "{x.status_code}" while making request to {request}')
                return []

        logger.log_multiline("SonarQube Issues:", self._format_issues(response_json))

        issues.extend(SonarIssue.parseIssues(response_json, self.already_fixed_files))

        return issues

    def _format_issues(self, issues):
        issues_data = json.loads(issues)
        table_format = "{:<60} {:<10} {:<60}"
        response = table_format.format("Message", "Severity", "Component")
        response += "\n" + ("-" * 130)
        for issue in issues_data.get("issues", []):
            response += "\n"
            response += table_format.format(
                issue["message"][:60], issue["severity"], issue["component"].split(":")[-1][:60]
            )
        return response
