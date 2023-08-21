from unittest.mock import Mock

import pytest
from unit.common.testing_issue import TestingIssue

from backends.query_backend import QueryBackend
from issues.issue_solver import IssueSolver
from proposals.diff_proposal import DiffProposal
from targets.diff_target import DiffTarget


# Create a concrete subclass of IssueSolver for testing
class ExampleIssueSolver(IssueSolver):
    def list_issues(self):
        # This method returns a list of issues, or a list of real IssueDescriptor objects with known characteristics.
        return []


# Define a fixture for the IssueSolver instance
@pytest.fixture
def issue_solver():
    return ExampleIssueSolver()


# Define a fixture for the diff_target mock
@pytest.fixture
def diff_target():
    return Mock(spec=DiffTarget)


# Define a fixture for the query_backend mock
@pytest.fixture
def query_backend():
    backend = Mock(spec=QueryBackend)
    backend.previous_backend.return_value = None
    return backend


# Define a fixture for the issue_descriptor mock
@pytest.fixture
def issue_descriptor():
    mock_issue = Mock(spec=TestingIssue)
    mock_issue.filename = "filename"
    mock_issue.issue_line = 1
    mock_issue.description = "description"
    mock_issue.list_proposals.return_value = []

    return mock_issue


@pytest.fixture
def proposal():
    proposal = Mock(spec=DiffProposal)
    proposal.try_fixing_with_priority_called = False
    proposal.try_fixing_with_priority_return_value = False

    def mock_impl(diff_target, query_backend, used_backend):
        proposal.try_fixing_with_priority_called = True
        return proposal.try_fixing_with_priority_return_value, query_backend

    proposal.try_fixing_with_priority = mock_impl
    return proposal


def test_solve_issues(issue_solver, diff_target, query_backend, issue_descriptor, proposal):
    issue_descriptor.list_proposals.return_value = [proposal]

    # Mock the issue_solver methods
    issue_solver.list_issues = Mock(return_value=[issue_descriptor])
    issue_solver.is_issue_fixed = Mock(return_value=True)

    # Mock the try_fixing_with_priority method to return True
    proposal.try_fixing_with_priority_return_value = True

    # Mock the commit_diff method to return True
    diff_target.commit_diff = Mock(return_value=True)
    diff_target.requires_refresh = Mock(return_value=False)

    issue_solver.solve_issues(diff_target, query_backend)

    # Check that the list_issues method was called once
    issue_solver.list_issues.assert_called()
    issue_solver.is_issue_fixed.assert_called()
    diff_target.commit_diff.assert_called()
    diff_target.revert_diff.assert_not_called()

    assert proposal.try_fixing_with_priority_called is True


def test_solve_issues_try_fixing_raises_exception(issue_solver, diff_target, query_backend, issue_descriptor, proposal):
    # Mock the list_issues method to return a list containing our mock issue
    issue_solver.list_issues = Mock(return_value=[issue_descriptor])

    issue_descriptor.list_proposals.return_value = [proposal]

    # Mock the try_fixing method to raise an exception
    proposal.try_fixing_with_priority = Mock(side_effect=Exception)
    # Mock the commit_diff method to return True
    diff_target.commit_diff = Mock(return_value=True)

    with pytest.raises(Exception):
        issue_solver.solve_issues(diff_target, query_backend)

    # Check that the list_issues method was called once
    issue_solver.list_issues.assert_called()

    # Check that the try_fixing method was called with the correct arguments
    proposal.try_fixing_with_priority.assert_called_once_with(
        diff_target=diff_target, query_backend=query_backend, used_backend=None
    )

    # Check that the commit_diff method was not called
    diff_target.commit_diff.assert_not_called()
    diff_target.revert_diff.assert_called()


def test_solve_issues_try_fixing_fails(issue_solver, diff_target, query_backend, issue_descriptor, proposal):
    # Mock the list_issues method to return a list containing our mock issue
    issue_solver.list_issues = Mock(return_value=[issue_descriptor])

    issue_descriptor.list_proposals.return_value = [proposal]

    # Mock the commit_diff method to return True
    diff_target.commit_diff = Mock(return_value=True)
    diff_target.revert_diff = Mock(return_value=None)

    issue_solver.solve_issues(diff_target, query_backend)

    # Check that the list_issues method was called once
    issue_solver.list_issues.assert_called()

    # Check that the try_fixing method was called with the correct arguments
    assert proposal.try_fixing_with_priority_called is True

    # Check that the commit_diff method was not called
    diff_target.commit_diff.assert_not_called()
    diff_target.revert_diff.assert_called()
