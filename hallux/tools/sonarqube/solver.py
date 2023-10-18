# Copyright: Hallux team, 2023

from __future__ import annotations

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

    def report_succesfull_fix(self, issue, proposal) -> None:
        self.already_fixed_files.append(issue.filename)
        self.backend.report_succesfull_fix(issue, proposal)


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
        extra_param: str | None = None,  # example: "branch=65-sonar-fixes"
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
        :param extra_param: It could be a path to a .json file, or a string with params
        """
        super().__init__(config_path, run_path, command_dir, validity_test=validity_test)

        if token is None:
            if os.getenv(self.SONAR_TOKEN) is not None:
                token = os.getenv(self.SONAR_TOKEN)

        self.token: Final[str | None] = token
        self.url: Final[str | None] = url
        self.project: Final[str | None] = project
        self.search_params: Final[str] = search_params
        self.extra_param: Final[str | None] = extra_param

        # With SonarQube we only may solve 1 issue per file.
        self.already_fixed_files: Final[list[str]] = []

    def solve_issues(self, diff_target: DiffTarget, query_backend: QueryBackend):
        if not self.token or not self.url or not self.project:
            logger.error("SonarQube: token, url or project not configured")

        else:
            logger.message("Process SonarQube issues:")
            new_query_backend = OverrideQueryBackend(query_backend, self.already_fixed_files)
            super().solve_issues(diff_target, new_query_backend)

    def list_issues(self) -> list[IssueDescriptor]:
        issues: list[IssueDescriptor] = []

        response_json: str
        if self.extra_param and self.extra_param.endswith(".json") and Path(self.extra_param).exists():
            logger.info("SONAR extra_params is a json file: " + self.extra_param)
            with open(self.extra_param, "r") as f:
                response_json = f.read()
        else:
            try:
                request: str = self.url + "/api/issues/search?" + self.search_params
                if self.extra_param is not None:
                    request += "&" + self.extra_param
                if self.project is not None:
                    request += "&componentKeys=" + self.project
                x = requests.get(url=request, headers={"Authorization": "Bearer " + self.token})
            except Exception:
                return []

            if x.status_code == 200:
                response_json = x.text
            else:
                logger.error(f'SonarQube: error "{x.status_code}" while making request to {request}')
                return []

        issues.extend(SonarIssue.parseIssues(response_json, self.already_fixed_files))

        return issues
