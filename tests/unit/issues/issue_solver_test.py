import pytest
from unittest.mock import Mock, call
from issues.issue_solver import IssueSolver
from issues.issue import IssueDescriptor
from proposals.diff_proposal import DiffProposal
from proposals.proposal_engine import ProposalEngine, ProposalList
from targets.diff_target import DiffTarget
from backend.query_backend import QueryBackend

from unit.common.test_issue import TestIssue


# Create a concrete subclass of IssueSolver for testing
class ExampleIssueSolver(IssueSolver):
    def list_issues(self):
        # This method could return a list of mock issues, or a list of real IssueDescriptor objects with known characteristics.
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
    return Mock(spec=QueryBackend)


# Define a fixture for the issue_descriptor mock
@pytest.fixture
def issue_descriptor():
    mock_issue = Mock(spec=TestIssue)
    mock_issue.filename = "filename"
    mock_issue.issue_line = 1
    mock_issue.description = "description"
    mock_issue.list_proposals.return_value = []

    return mock_issue


@pytest.fixture
def proposal():
    proposal = Mock(spec=DiffProposal)
    proposal.try_fixing.return_value = True
    return proposal


def test_solve_issues(issue_solver, diff_target, query_backend, issue_descriptor, proposal):
    issue_descriptor.list_proposals.return_value = [proposal]

    # Mock the list_issues method to return a list containing our mock issue
    issue_solver.list_issues = Mock(return_value=[issue_descriptor])

    # Mock the try_fixing method to return True
    proposal.try_fixing = Mock(return_value=True)

    # Mock the commit_diff method to return True
    diff_target.commit_diff = Mock(return_value=True)

    issue_solver.solve_issues(diff_target, query_backend)

    # Check that the list_issues method was called once
    issue_solver.list_issues.assert_called()

    # Check that the try_fixing method was called with the correct arguments
    proposal.try_fixing.assert_called_once_with(diff_target=diff_target, query_backend=query_backend)


def test_solve_issues_try_fixing_raises_exception(issue_solver, diff_target, query_backend, issue_descriptor, proposal):
    # Mock the list_issues method to return a list containing our mock issue
    issue_solver.list_issues = Mock(return_value=[issue_descriptor])

    issue_descriptor.list_proposals.return_value = [proposal]

    # Mock the try_fixing method to raise an exception
    proposal.try_fixing = Mock(side_effect=Exception)
    # Mock the commit_diff method to return True
    diff_target.commit_diff = Mock(return_value=True)

    with pytest.raises(Exception):
        issue_solver.solve_issues(diff_target, query_backend)

    # Check that the list_issues method was called once
    issue_solver.list_issues.assert_called()

    # Check that the try_fixing method was called with the correct arguments
    proposal.try_fixing.assert_called_once_with(diff_target=diff_target, query_backend=query_backend)

    # Check that the commit_diff method was not called
    diff_target.commit_diff.assert_not_called()


def test_solve_issues_try_fixing_fails(issue_solver, diff_target, query_backend, issue_descriptor):
    # Mock the list_issues method to return a list containing our mock issue
    issue_solver.list_issues = Mock(return_value=[issue_descriptor])

    issue_descriptor.list_proposals.return_value = [proposal]

    # Mock the try_fixing method to return False
    proposal.try_fixing = Mock(return_value=False)
    # Mock the commit_diff method to return True
    diff_target.commit_diff = Mock(return_value=True)

    issue_solver.solve_issues(diff_target, query_backend)

    # Check that the list_issues method was called once
    issue_solver.list_issues.assert_called()

    # Check that the try_fixing method was called with the correct arguments
    proposal.try_fixing.assert_called_once_with(diff_target=diff_target, query_backend=query_backend)

    # Check that the commit_diff method was not called
    diff_target.commit_diff.assert_not_called()


def test_solve_issues_try_fixing_succeeds(issue_solver, diff_target, query_backend, issue_descriptor):
    # Mock the list_issues method to return a list containing our mock issue the first time,
    # and an empty list the second time
    issue_solver.list_issues = Mock(side_effect=[[issue_descriptor], [], []])
    issue_descriptor.list_proposals.return_value = [proposal]
    # Mock the try_fixing method to return True
    proposal.try_fixing = Mock(return_value=True)
    # Mock the commit_diff method to return True
    diff_target.commit_diff = Mock(return_value=True)

    issue_solver.solve_issues(diff_target, query_backend)

    # Check that the list_issues method was called once
    issue_solver.list_issues.assert_called()

    # Check that the try_fixing method was called with the correct arguments
    proposal.try_fixing.assert_called_once_with(diff_target=diff_target, query_backend=query_backend)

    # Check that the commit_diff method was called once
    diff_target.commit_diff.assert_called_once()