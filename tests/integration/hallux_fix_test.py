#!/bin/env python
# Copyright: Hallux team, 2023

# HALLUX FIX TEST : checks that `hallux fix` command indeed capable of fixing all issues in the test-project(s)
from __future__ import annotations
import tempfile
import pytest
import shutil
import os
from pathlib import Path
import subprocess
from code_processor import set_directory
from utils.logger import logger

env = os.environ.copy()

def test_hallux_fix_cpp(
<<<<<<< HEAD
    real_openai_test: bool, proj_name: str = "test-cpp-project", tmp_proj_dir: str | None = None, target: str = ""
||||||| parent of 262ae91 (#22 addinig logget WIP)
    real_openai_test: bool, proj_name: str = "test-cpp-project", tmp_proj_dir: str | None = None, command: str = "fix"
=======
    real_openai_test: bool = False, proj_name: str = "test-cpp-project", tmp_proj_dir: str | None = None, command: str = "fix"
>>>>>>> 262ae91 (#22 addinig logget WIP)
):
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
    cmake_tmp_path = Path(cmake_tmp_dir)

    # check that temporal project has c++ compilation issues
    with set_directory(cmake_tmp_path):
        try:
            print("cmake", tmp_proj_dir, "...")
            print(cmake_tmp_path.cwd())
            print(cmake_tmp_path.cwd())
            # logger.debug(f"cmake {tmp_proj_dir}")
            # subprocess.check_output(["ls", "-la", tmp_proj_dir])
            # subprocess.check_output(["ls", "-la", tmp_proj_dir])
            subprocess.check_output(["cmake", tmp_proj_dir])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # cmake must not fail

        make_succesfull: bool = True
        try:
            print("make cpp/test_cpp_project.o...")
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
        if real_config_file.exists():
            if dummy_config_file.exists():
                dummy_config_file.unlink()
            real_config_file.rename(dummy_config_file)

    # run hallux from the temporal project directory
    with set_directory(Path(tmp_proj_dir)):
        try:
            subprocess.check_output(["hallux", "fix", target])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # hallux must not fail ?

    # ASSERT: must be no remaining c++ compilation issues
    with set_directory(Path(cmake_tmp_dir)):
        try:
            subprocess.check_output(["make", "cpp/test_cpp_project.o"], stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # make must not find any issues


<<<<<<< HEAD
def test_hallux_fix_python(
    real_openai_test: bool,
    proj_name: str = "test-python-project",
    tmp_proj_dir: str | None = None,
    target: str = "--files",
):
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
        if real_config_file.exists():
            if dummy_config_file.exists():
                dummy_config_file.unlink()
            real_config_file.rename(dummy_config_file)

    # run hallux from the temporal project directory
    with set_directory(Path(tmp_proj_dir)):
        try:
            subprocess.check_output(["hallux", "fix", target])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # hallux must not fail ?

        # ASSERT: ruff must have no remaining issues
        try:
            subprocess.check_output(["ruff", "check", "."])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # ruff must not find any issues
||||||| parent of 262ae91 (#22 addinig logget WIP)
def test_hallux_fix_python(
    real_openai_test: bool,
    proj_name: str = "test-python-project",
    tmp_proj_dir: str | None = None,
    command: str = "fix",
):
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
        if real_config_file.exists():
            if dummy_config_file.exists():
                dummy_config_file.unlink()
            real_config_file.rename(dummy_config_file)

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
=======
# def test_hallux_fix_python(
#     real_openai_test: bool,
#     proj_name: str = "test-python-project",
#     tmp_proj_dir: str | None = None,
#     command: str = "fix",
# ):
#     # Create temporal dir, if not already exists
#     if tmp_proj_dir is None:
#         if not Path("/tmp/hallux").exists():
#             Path("/tmp/hallux").mkdir()
#         tmp_proj_dir = tempfile.mkdtemp(dir="/tmp/hallux")

#     # original/reference test-project directory
#     proj_dir = Path(__file__).resolve().parent.parent.joinpath(proj_name)

#     # copy reference project into temp folder
#     shutil.copytree(str(proj_dir), tmp_proj_dir, ignore_dangling_symlinks=False, dirs_exist_ok=True)

#     # check that temporal project has ruff issues
#     with set_directory(Path(tmp_proj_dir)):
#         returncode: int = 0
#         try:
#             subprocess.check_output(["ruff", "check", "."])
#         except subprocess.CalledProcessError as e:
#             returncode = e.returncode

#         assert returncode != 0, f"Initial state of {proj_name} contains no ruff warnings"

#     if real_openai_test:
#         print("REAL OPENAI TEST")
#         dummy_config_file = Path(tmp_proj_dir).joinpath(".hallux")
#         real_config_file = Path(tmp_proj_dir).joinpath(".hallux.real")
#         if real_config_file.exists():
#             if dummy_config_file.exists():
#                 dummy_config_file.unlink()
#             real_config_file.rename(dummy_config_file)

#     # run hallux from the temporal project directory
#     with set_directory(Path(tmp_proj_dir)):
#         try:
#             subprocess.check_output(["hallux", command])
#         except subprocess.CalledProcessError as e:
#             pytest.fail(e, pytrace=True)  # hallux must not fail ?

#         # ASSERT: ruff must have no remaining issues
#         try:
#             subprocess.check_output(["ruff", "check", "."])
#         except subprocess.CalledProcessError as e:
#             pytest.fail(e, pytrace=True)  # ruff must not find any issues


test_hallux_fix_cpp()
>>>>>>> 262ae91 (#22 addinig logget WIP)
