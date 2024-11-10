import pytest
from hallux.proposals.diff_proposal import DiffProposal
from unittest.mock import patch, MagicMock
from io import StringIO


class CustomProposal(DiffProposal):
    def try_fixing(self, query_backend, diff_target) -> bool:
        return True


@pytest.fixture(scope="session")
def custom_proposal():
    return CustomProposal("test-file.py", "description")


@patch("sys.stdout", new_callable=StringIO)
def test_print_diff(mock_stdout, custom_proposal):
    # Set up input lines
    lines1 = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5", "Line 6"]
    lines2 = [
        "Line 1 modified",
        "Line 2",
        "Line 4",
        "Line 6",
        "Line 7",
    ]

    custom_proposal.print_diff(lines1, lines2)
    diff_lines = [line.strip() for line in mock_stdout.getvalue().splitlines()]
    expected_lines = [
        "\x1b[91m--- test-file.py",
        "\x1b[0m",
        "\x1b[92m+++ test-file.py",
        "\x1b[0m",
        "@@ -1,6 +1,5 @@",
        "",
        "\x1b[91m-Line 1\x1b[0m",
        "\x1b[92m+Line 1 modified\x1b[0m",
        "Line 2",
        "\x1b[91m-Line 3\x1b[0m",
        "Line 4",
        "\x1b[91m-Line 5\x1b[0m",
        "Line 6",
        "\x1b[92m+Line 7\x1b[0m",
    ]

    assert diff_lines == expected_lines


def test_try_fixing_with_priority_return_true(custom_proposal):
    def first_backend():
        return None

    def second_backend():
        return MagicMock(previous_backend=first_backend)

    query_backend = MagicMock(previous_backend=second_backend)
    diff_target = "test-file.py"
    used_backend = "some-other-backend"

    result = custom_proposal.try_fixing_with_priority(query_backend, diff_target, used_backend)
    assert result[0] is True
