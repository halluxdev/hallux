import os
from pathlib import Path
from typing import Final
from unittest.mock import Mock, patch

import pytest
import requests

from hallux.backends.query_backend import QueryBackend
from hallux.issues.issue import IssueDescriptor
from hallux.targets.diff import DiffTarget
from hallux.tools.sonarqube.solver import OverrideQueryBackend, Sonar_IssueSolver, SonarIssue

SONAR_SAMPLE_TOKEN: Final[str] = "sqt-deadbeefdeadbeefdeadbeefdeadbeef"
SONAR_PROJECT: Final[str] = "test_project"


@pytest.fixture
def solver_instance():
    # Mock the __init__ method to avoid any side effects during instantiation
    with patch.object(Sonar_IssueSolver, "__init__", lambda x, *args, **kwargs: None):
        # Instantiate the object without calling the actual __init__
        instance = Sonar_IssueSolver.__new__(Sonar_IssueSolver)

        instance.search_params = "mock_search_params"
        instance.argvalue = "mock_extra_param"
        instance.already_fixed_files = []
        return instance


# Tests for Sonar_IssueSolver
def test_sonar_with_json_file():
    sonar_solver = Sonar_IssueSolver(
        config_path=Path(__file__).resolve().parent,
        run_path=Path(__file__).resolve().parent,
        argvalue=str(Path(__file__).resolve().parent.joinpath("sonar_example.json")),
    )

    issues = sonar_solver.list_issues()
    assert len(issues) == 13
    assert isinstance(issues[0], SonarIssue)
    issues[0].issue_type == "CODE SMELL"
    issues[0].filename == "hallux/auxilary.py"


# Tests for Sonar_IssueSolver
def test_list_issues():
    print(os.getcwd())

    with patch.object(requests, "get") as mocked_get:
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.text = '{"issues": []}'

        sonar_solver = Sonar_IssueSolver(
            Path(), Path(), url="http://localhost", token=SONAR_SAMPLE_TOKEN, project=SONAR_PROJECT
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
            Path(), Path(), url="http://localhost", token=SONAR_SAMPLE_TOKEN, project="test_project"
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


def test_solve_issues_with_missing_configuration(solver_instance, caplog):
    solver_instance.token = None  # Simulate missing token
    solver_instance.url = "http://example.com"
    solver_instance.project = "example_project"

    with caplog.at_level("ERROR"):
        solver_instance.solve_issues(None, None)
        assert any("SonarQube: token, url or project not configured" in message for message in caplog.text.splitlines())


def test_solve_issues_with_full_configuration(solver_instance, caplog):
    solver_instance.token = "mock_token"
    solver_instance.url = "mock_url"
    solver_instance.project = "mock_project"

    diff_target = Mock(spec=DiffTarget)
    query_backend = Mock(spec=QueryBackend)

    # with patch('hallux.tools.sonarqube.solver.OverrideQueryBackend', autospec=True) as mock_override_backend:
    # with patch.object(Sonar_IssueSolver, 'solve_issues', autospec=True) as mock_super_solve_issues:
    with caplog.at_level("INFO"):
        solver_instance.solve_issues(diff_target, query_backend)

        # Assert log message
        # assert any("2222" in message for message in caplog.text.splitlines())
        # assert any("Process SonarQube issues:" in message for message in caplog.text.splitlines())

        # Assert OverrideQueryBackend was called with the right parameters
        # mock_override_backend.assert_called_once_with(query_backend, solver_instance.already_fixed_files)

        # Assert the super solve_issues method was called
        # mock_super_solve_issues.assert_called_once_with(solver_instance, diff_target, mock_override_backend.return_value)
