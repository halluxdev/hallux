#!/bin/env python
# Copyright: Hallux team, 2023

# HALLUX TEST : checks that `hallux .` command indeed capable of fixing all issues in the test-project(s)
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from auxilary import set_directory


def test_hallux_cpp(
    real_openai_test: bool = False,
    proj_name: str = "test-cpp-project",
    tmp_proj_dir: str | None = None,
    target: str = "--files",
):
    backend = "--gpt3" if real_openai_test else "--cache"
    # Create temporal dir, if not already exists
    if tmp_proj_dir is None:
        if not Path("/tmp/hallux").exists():
            Path("/tmp/hallux").mkdir()
        tmp_proj_dir = tempfile.mkdtemp(dir="/tmp/hallux")

    # original/reference test-project directory
    proj_dir = Path(__file__).resolve().parent.parent.joinpath(proj_name)

    # copy reference project into temp folder
    shutil.copytree(str(proj_dir), tmp_proj_dir, ignore_dangling_symlinks=False, dirs_exist_ok=True)

    # temporal dir for cmake init
    cmake_tmp_dir = tempfile.mkdtemp(dir="/tmp/hallux")

    # check that temporal project has c++ compilation issues
    with set_directory(Path(cmake_tmp_dir)):
        try:
            subprocess.check_output(["cmake", tmp_proj_dir])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # cmake must not fail

        make_succesfull: bool = True
        try:
            subprocess.check_output(["make", "cpp/test_cpp_project.o"], stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            make_succesfull = False
            returncode = e.returncode

    assert not make_succesfull, f"Initial state of {proj_name} Have no issues for cpp/test_cpp_project.o"
    assert returncode == 2

    if real_openai_test:
        print("REAL OPENAI TEST")
        dummy_config_file = Path(tmp_proj_dir).joinpath(".hallux")
        real_config_file = Path(tmp_proj_dir).joinpath(".hallux.real")
        Path(tmp_proj_dir).joinpath("dummy.json").unlink()
        if real_config_file.exists():
            if dummy_config_file.exists():
                dummy_config_file.unlink()
            real_config_file.rename(dummy_config_file)

    # run hallux from the temporal project directory
    with set_directory(Path(tmp_proj_dir)):
        try:
            subprocess.check_output(["hallux", target, backend, "."])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # hallux must not fail ?

    # ASSERT: must be no remaining c++ compilation issues
    with set_directory(Path(cmake_tmp_dir)):
        try:
            subprocess.check_output(["make", "cpp/test_cpp_project.o"], stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # make must not find any issues


def test_hallux_python(
    real_openai_test: bool = False,
    proj_name: str = "test-python-project",
    tmp_proj_dir: str | None = None,
    target: str = "--files",
):
    backend = "--gpt3" if real_openai_test else "--cache"
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

    if real_openai_test:
        print("REAL OPENAI TEST")
        dummy_config_file = Path(tmp_proj_dir).joinpath(".hallux")
        real_config_file = Path(tmp_proj_dir).joinpath(".hallux.real")
        Path(tmp_proj_dir).joinpath("dummy.json").unlink()
        if real_config_file.exists():
            if dummy_config_file.exists():
                dummy_config_file.unlink()
            real_config_file.rename(dummy_config_file)

    # run hallux from the temporal project directory
    with set_directory(Path(tmp_proj_dir)):
        try:
            subprocess.check_output(["hallux", target, backend, "."])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # hallux must not fail ?

        # ASSERT: ruff must have no remaining issues
        try:
            subprocess.check_output(["ruff", "check", "."])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # ruff must not find any issues
