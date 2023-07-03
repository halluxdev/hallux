#!/bin/env python
# Copyright: Hallux team, 2023

# HALLUX FIX TEST : checks that `hallux fix` command indeed capable of fixing all issues in the test-project(s)
from __future__ import annotations
import tempfile
import pytest
import shutil
from pathlib import Path
import subprocess
from code_processor import set_directory


def test_hallux_fix(proj_name: str = "test-python-project", tmp_proj_dir: str | None = None, command: str = "fix"):
    # Create temporal dir, if not already exists
    if tmp_proj_dir is None:
        if not Path("/tmp/hallux").exists():
            Path("/tmp/hallux").mkdir()
        tmp_proj_dir = tempfile.mkdtemp(dir="/tmp/hallux")

    # original/reference test-project directory
    proj_dir = Path(__file__).resolve().parent.parent.joinpath(proj_name)

    # copy reference project into temp folder
    shutil.copytree(str(proj_dir), tmp_proj_dir, ignore_dangling_symlinks=False, dirs_exist_ok=True)

    # check that temporal project has ruff issues
    with set_directory(Path(tmp_proj_dir)):
        returncode: int = 0
        try:
            subprocess.check_output(["ruff", "check", "."])
        except subprocess.CalledProcessError as e:
            returncode = e.returncode

        assert returncode != 0, f"Initial state of {proj_name} contains no ruff warnings"

    # temporal dir for cmake init
    # cmake_tmp_dir = tempfile.mkdtemp(dir="/tmp/hallux")

    # # check that temporal project has c++ compilation issues
    # with set_directory(Path(cmake_tmp_dir)):
    #     try:
    #         subprocess.check_output(["cmake", tmp_proj_dir])
    #     except subprocess.CalledProcessError as e:
    #         pytest.fail(e, pytrace=True)  # cmake must not fail

    #     make_succesfull: bool = True
    #     try:
    #         subprocess.check_output(["make", "cpp/test_cpp_project.o"])
    #     except subprocess.CalledProcessError as e:
    #         make_succesfull = False
    #         returncode = e.returncode

    # assert not make_succesfull, f"Initial state of {proj_name} Have no issues for cpp/test_cpp_project.o"
    # assert returncode == 2

    # run hallux from the temporal project directory
    with set_directory(Path(tmp_proj_dir)):
        try:
            subprocess.check_output(["hallux", command])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # hallux must not fail ?

        # ASSERT: ruff must have no remaining issues
        try:
            subprocess.check_output(["ruff", "check", "."])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # ruff must not find any issues

    # ASSERT: must be no remaining c++ compilation issues
    # with set_directory(Path(cmake_tmp_dir)):
    #     try:
    #         subprocess.check_output(["make", "cpp/test_cpp_project.o"])
    #     except subprocess.CalledProcessError as e:
    #         pytest.fail(e, pytrace=True)  # make must not find any issues
