#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from typing import Final
from unittest.mock import MagicMock, patch, mock_open

import pytest

from targets.filesystem_target import FilesystemTarget
from file_diff import FileDiff


def test_filesystem_target():
    with patch("builtins.open", mock_open(read_data="1\n2\n3\n4\n5")) as mock_file:
        filename: Final[str] = "/tmp/hallux_mocked_test_file.txt"
        # create FileDiff
        filediff = FileDiff(filename, issue_line=3, radius=1)

        # check that filediff has all fields correctly set
        assert filediff.filename == filename
        assert filediff.issue_line == 3
        assert len(filediff.all_lines) == 5
        assert filediff.all_lines == ["1", "2", "3", "4", "5"]
        assert len(filediff.issue_lines) == 3
        assert filediff.issue_lines == ["2", "3", "4"]
        assert len(filediff.proposed_lines) == 0

        # proposing lines
        filediff.propose_lines("2A\n3A\n4A\nX")
        assert len(filediff.proposed_lines) == 4

        # helper to check what was written back into file
        global written_text
        written_text = ""

        def write_side_effect(*args, **kwargs):
            global written_text
            written_text = written_text + args[0]

        mock_file.return_value.write.side_effect = write_side_effect

        # create FilesystemTarget and call apply_diff
        fs_target = FilesystemTarget()
        fs_target.apply_diff(filediff)

        # written text shall contain proposed lines
        assert written_text.split("\n") == ["1", "2A", "3A", "4A", "X", "5"]

        try:
            fs_target.apply_diff(filediff)
            pytest.fail("Second call of apply_diff must cause an Exception")
        except Exception:
            pass  # everything is OK
        except:
            pytest.fail("Only Exception is allowed here")

        # call revert_diff - file shall have original lines
        written_text = ""
        fs_target.revert_diff()
        assert written_text.split("\n") == ["1", "2", "3", "4", "5"]
