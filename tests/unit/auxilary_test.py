#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

import os
import tempfile

import pytest

from hallux.auxilary import Path, find_arg, find_argvalue, set_directory


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


@pytest.mark.parametrize(
    "args, look_for, expect_value",
    [
        ([], "aaaa", None),
        (["aaa", "bbb"], "bbb", None),
        (["hallux", "--python", "--aaaa"], "--python", None),
    ],
)
def test_find_argvalue(args: list[str], look_for: str, expect_value: str | None):
    found_value = find_argvalue(args, look_for)
    assert found_value == expect_value


def test_set_directory():
    current_dir = str(Path().absolute())
    tmp_dir = Path(tempfile.mkdtemp())

    with set_directory(tmp_dir):
        assert os.getcwd() == os.path.realpath(tmp_dir)

    assert os.getcwd() == current_dir
