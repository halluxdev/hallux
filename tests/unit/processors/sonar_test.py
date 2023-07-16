from typing import Final
import requests
from unittest.mock import Mock, patch
from pathlib import Path
from issue import IssueDescriptor
from processors.sonar import Sonar_IssueSolver, SonarIssue


SONAR_SAMPLE_TOKEN: Final[str] = "sqt-deadbeefdeadbeefdeadbeefdeadbeef"


# Tests for Sonar_IssueSolver
def test_list_issues():
    with patch.object(requests, "get") as mocked_get:
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.text = '{"issues": []}'

        sonar_solver = Sonar_IssueSolver(url="http://localhost", token=SONAR_SAMPLE_TOKEN, project="test_project")
        issues = sonar_solver.list_issues()

        assert issues == []
        mocked_get.assert_called_once_with(
            url="http://localhost/api/issues/search?resolved=false&severities=MINOR,MAJOR,CRITICAL&statuses=OPEN,CONFIRMED,REOPENED&componentKeys=hallux",
            headers={"Authorization": "Bearer " + SONAR_SAMPLE_TOKEN},
        )


def test_list_issues_bad_response():
    with patch.object(requests, "get") as mocked_get:
        mocked_get.return_value.status_code = 404

        sonar_solver = Sonar_IssueSolver(url="http://localhost", token=SONAR_SAMPLE_TOKEN, project="test_project")
        issues = sonar_solver.list_issues()

        assert issues == []


# Tests for SonarIssue
def test_try_fixing_no_results(filename="file_diff_test.txt"):
    query_backend = Mock()
    query_backend.query.return_value = []

    diff_target = Mock()
    diff_target.apply_diff.return_value = False

    test_file = Path(__file__).resolve().parent.parent.joinpath(filename)

    sonar_issue = SonarIssue(
        filename=str(test_file.absolute()),
        text_range={"startLine": 2, "startOffset": 0, "endLine": 2, "endOffset": 0},
        issue_line=2,
    )
    result = sonar_issue.try_fixing(query_backend, diff_target)

    assert not result


def test_parse_issues():
    request_output = '{"issues": [{"component": "component:test_file", "line": 1, "message": "message", "textRange": {"startLine": 1, "startOffset": 0, "endLine": 1, "endOffset": 0}, "type": "type"}]}'

    issues = SonarIssue.parseIssues(request_output)

    assert len(issues) == 1
    assert isinstance(issues[0], IssueDescriptor)
    assert issues[0].filename == "test_file"
    assert issues[0].issue_line == 1
    assert issues[0].description == "message"
    assert issues[0].issue_type == "type"
