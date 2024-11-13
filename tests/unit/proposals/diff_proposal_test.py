from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from hallux.proposals.diff_proposal import DiffProposal


class CustomProposal(DiffProposal):
    def try_fixing(self, query_backend, diff_target) -> bool:
        return True


@pytest.fixture(scope="session")
def custom_proposal():
    return CustomProposal("test-file.py", "description")


@patch("sys.stdout", new_callable=StringIO)
def test_print_diff(mock_stdout, custom_proposal):
    # Set up input lines
    lines1 = ["Line 1\n", "Line 2\n", "Line 3\n", "Line 4\n", "Line 5\n", "Line 6\n"]
    lines2 = [
        "Line 1 modified\n",
        "Line 2\n",
        "Line 4\n",
        "Line 6\n",
        "Line 7\n",
    ]

    custom_proposal.print_diff(lines1, lines2)
    diff_lines = [line.strip() for line in mock_stdout.getvalue().splitlines()]
    expected_lines = [
        "\x1b[91m--- test-file.py",
        "\x1b[0m\x1b[92m+++ test-file.py",
        "\x1b[0m@@ -1,6 +1,5 @@",
        "\x1b[91m-Line 1",
        "\x1b[0m\x1b[92m+Line 1 modified",
        "\x1b[0m Line 2",
        "\x1b[91m-Line 3",
        "\x1b[0m Line 4",
        "\x1b[91m-Line 5",
        "\x1b[0m Line 6",
        "\x1b[92m+Line 7",
        "\x1b[0m",
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
