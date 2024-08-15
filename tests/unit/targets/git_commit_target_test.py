from typing import Final
from unittest.mock import Mock, patch

import pytest

from hallux.targets.filesystem import FilesystemTarget
from hallux.targets.git_commit import GitCommitTarget

TEST_PROJECT_PATH: Final[str] = "/current/dir"


@pytest.fixture
def filesystem_target():
    mock_filesystem = Mock()
    mock_filesystem.apply_diff.return_value = True
    return mock_filesystem


@pytest.fixture
def diff_proposal():
    mock_diff = Mock()
    mock_diff.description = "description"
    mock_diff.filename = "/path/to/file"
    return mock_diff


@pytest.fixture
def git_target_factory():
    def response(output=b""):
        with patch("subprocess.check_output") as mock_subprocess_check_output:
            mock_subprocess_check_output.return_value = output
            mock_git_target = GitCommitTarget()

        return mock_git_target

    return response


# Test that GitCommitTarget raises an error if there are uncommitted changes in the repo
def test_init_error(git_target_factory):
    with pytest.raises(SystemError):
        git_target_factory(b"not empty")


def test_apply_diff(git_target_factory, diff_proposal):
    with patch.object(FilesystemTarget, "apply_diff", return_value=True) as mock_fs_apply_diff:
        git_target = git_target_factory()
        result = git_target.apply_diff(diff_proposal)
    mock_fs_apply_diff.assert_called_once_with(git_target, diff_proposal)
    assert result is True


def test_revert_diff(git_target_factory):
    with patch.object(FilesystemTarget, "revert_diff") as mock_fs_target:
        git_target = git_target_factory()
        git_target.revert_diff()
    mock_fs_target.assert_called_once_with(git_target)


def test_requires_refresh(git_target_factory):
    git_target = git_target_factory()
    result = git_target.requires_refresh()
    assert result is True


def test_commit_diff(git_target_factory, diff_proposal):
    with (
        patch("subprocess.check_output") as mock_subprocess,
        patch.object(FilesystemTarget, "revert_diff", return_value=None),
        patch("os.getcwd", return_value=TEST_PROJECT_PATH),
        patch("os.chdir") as mock_chdir,
    ):
        git_target = git_target_factory()
        git_target.existing_proposal = diff_proposal

        mock_subprocess.return_value = b""

        # Assertions
        assert git_target.commit_diff() is True

        # Check that subprocess.check_output was called with the expected arguments
        mock_subprocess.assert_any_call(["git", "add", "file"])
        mock_subprocess.assert_any_call(["git", "commit", "-m", f"HALLUX: {diff_proposal.description}"])

        # Check that os.chdir was called to change into and back out of the git directory
        mock_chdir.assert_any_call("/path/to")
        mock_chdir.assert_any_call(TEST_PROJECT_PATH)


# Coverage with verbose = True
def test_commit_diff_verbose(git_target_factory, diff_proposal):
    with (
        patch("subprocess.check_output"),
        patch.object(FilesystemTarget, "revert_diff", return_value=None),
        patch("os.getcwd", return_value=TEST_PROJECT_PATH),
        patch("os.chdir"),
    ):
        git_target = git_target_factory()
        git_target.existing_proposal = diff_proposal
        git_target.verbose = True
        assert git_target.commit_diff() is True


def test_commit_diff_failure(git_target_factory, diff_proposal):
    with (
        patch.object(FilesystemTarget, "revert_diff", return_value=None) as mock_fs_revert_diff,
        patch("os.getcwd", return_value=TEST_PROJECT_PATH),
        patch("os.chdir"),
    ):
        git_target = git_target_factory()
        git_target.existing_proposal = diff_proposal

        assert git_target.commit_diff() is False
        mock_fs_revert_diff.assert_called_once_with(git_target)


# Coverage with verbose = True


def test_commit_diff_failure_verbose(git_target_factory, diff_proposal):
    with (
        patch.object(FilesystemTarget, "revert_diff", return_value=None),
        patch("os.getcwd", return_value=TEST_PROJECT_PATH),
        patch("os.chdir"),
    ):
        git_target = git_target_factory()
        git_target.existing_proposal = diff_proposal
        git_target.verbose = True

        assert git_target.commit_diff() is False
