#!/bin/env python
# Copyright: Hallux team, 2023

# HALLUX TEST : checks that `hallux .` command indeed capable of fixing all issues in the test-project(s)
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
from utils import hallux_tmp_dir

from hallux.auxilary import set_directory
from hallux.main import main


def test_hallux_sonar_swift(
    real_openai_test: bool = True,
    proj_name: str = "test-swift-project",
    tmp_proj_dir: str | None = None,
    target: str = "--files",
):
    backend = "--model=gpt-4o-mini" if real_openai_test else "--cache"

    # Create project dir, if not already provided
    if tmp_proj_dir is None:
        tmp_dir = hallux_tmp_dir()
        tmp_proj_dir = tmp_dir.name

    # original/reference test-project directory
    proj_dir = Path(__file__).resolve().parent.parent.joinpath(proj_name)

    # copy reference project into temp folder
    shutil.copytree(str(proj_dir), tmp_proj_dir, ignore_dangling_symlinks=False, dirs_exist_ok=True)
    print(tmp_proj_dir)

    # run hallux from the temporal project directory
    with set_directory(tmp_proj_dir):
        try:
            main(["hallux", "--sonar=./sonar.json", "--verbose", target, backend, "."])
        except Exception as e:
            pytest.fail(e, pytrace=True)  # hallux must not fail ?
