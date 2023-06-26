#!/bin/env python
# Copyright: Hallux team, 2023

# TEST

import tempfile
import pytest
import shutil
import os
from pathlib import Path
import subprocess

def test_hallux_fix_ruff(proj_name: str = "test-project1"):
    if not Path("/tmp/hallux").exists():
        Path("/tmp/hallux").mkdir()

    tmp_dir = tempfile.mkdtemp(dir="/tmp/hallux")
    proj_dir = Path(__file__).resolve().parent.joinpath(proj_name)
    shutil.copytree(str(proj_dir), tmp_dir, ignore_dangling_symlinks=False, dirs_exist_ok=True)
    os.chdir(tmp_dir)
    returncode : int = 0
    try:
        subprocess.check_output(["ruff", "check", "."])
    except subprocess.CalledProcessError as e:
        returncode = e.returncode

    assert returncode != 0, f"Initial state of {proj_name} contains no ruff warnings"

    try:
        subprocess.check_output(["hallux", "fix"])
    except subprocess.CalledProcessError as e:
        pytest.fail(e, pytrace=True) # hallux must not fail ?

    try:
        subprocess.check_output(["ruff", "check", "."])
    except subprocess.CalledProcessError as e:
        pytest.fail(e, pytrace=True) # ruff must not find any issues



