import os
from pathlib import Path
from typing import Final
from unittest.mock import Mock, patch

import requests

from hallux.issues.issue import IssueDescriptor
from hallux.tools.sonarqube.solver import Sonar_IssueSolver, SonarIssue

SONAR_SAMPLE_TOKEN: Final[str] = "sqt-deadbeefdeadbeefdeadbeefdeadbeef"
SONAR_PROJECT: Final[str] = "test_project"


# Tests for Sonar_IssueSolver
def test_list_issues():
    print(os.getcwd())

    with patch.object(requests, "get") as mocked_get:
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.text = '{"issues": []}'

        sonar_solver = Sonar_IssueSolver(
            Path(), Path(), True, url="http://localhost", token=SONAR_SAMPLE_TOKEN, project=SONAR_PROJECT
        )
        issues = sonar_solver.list_issues()

        assert issues == []
        mocked_get.assert_called_once_with(
            url="http://localhost/api/issues/search?resolved=false&severities=MINOR,MAJOR,CRITICAL"
            + "&statuses=OPEN,CONFIRMED,REOPENED&componentKeys="
            + SONAR_PROJECT,
            headers={"Authorization": "Bearer " + SONAR_SAMPLE_TOKEN},
        )


def test_list_issues_bad_response():
    with patch.object(requests, "get") as mocked_get:
        mocked_get.return_value.status_code = 404

        sonar_solver = Sonar_IssueSolver(
            Path(), Path(), False, url="http://localhost", token=SONAR_SAMPLE_TOKEN, project="test_project"
        )
        issues = sonar_solver.list_issues()

        assert issues == []


# Tests for SonarIssue
def test_try_fixing_no_results(filename=__file__):
    query_backend = Mock()
    query_backend.query.return_value = []

    diff_target = Mock()
    diff_target.apply_diff.return_value = False

    test_file = Path(__file__).resolve().parent.parent.joinpath(filename)

    sonar_issue = SonarIssue(
        filename=str(test_file.absolute()),
        text_range={"startLine": 2, "endLine": 2, "startOffset": 0, "endOffset": 0},
        issue_line=2,
    )
    proposals = sonar_issue.list_proposals()
    proposal = next(proposals)
    result = proposal.try_fixing(query_backend, diff_target)

    assert not result


def test_parse_issues():
    request_output = (
        '{"issues": [{"component": "component:test_file", "line": 1, "message": "message", "textRange": {"startLine":'
        ' 1, "startOffset": 0, "endLine": 1, "endOffset": 0}, "type": "type"}]}'
    )

    issues = SonarIssue.parseIssues(request_output, [])

    assert len(issues) == 1
    assert isinstance(issues[0], IssueDescriptor)
    assert issues[0].filename == "test_file"
    assert issues[0].issue_line == 1
    assert issues[0].description == "message"
    assert issues[0].issue_type == "type"
