#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations
import pytest
import os
import tempfile
from auxilary import set_directory, find_arg, Path


@pytest.mark.parametrize(
    "args, look_for, expect_index",
    [
        ([], "aaaa", -1),
        (["aaa", "bbb"], "bbb", 1),
        (["hallux", "--python", "--aaaa"], "--python", 1),
    ],
)
def test_find_arg(args: list[str], look_for: str, expect_index):
    found_index = find_arg(args, look_for)
    assert found_index == expect_index


def test_set_directory():
    current_dir = str(Path().absolute())
    tmp_dir = Path(tempfile.mkdtemp())

    with set_directory(tmp_dir):
        assert os.getcwd() == str(tmp_dir.absolute())

    assert os.getcwd() == current_dir
