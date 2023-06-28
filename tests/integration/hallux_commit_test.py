#!/bin/env python
# Copyright: Hallux team, 2023

# HALLUX COMMIT TEST : checks that `hallux fix` command indeed capable of fixing all issues in the test-project(s)
from __future__ import annotations

import tempfile
import pytest
import shutil
from pathlib import Path
import subprocess
from code_processor import set_directory

from integration.hallux_fix_test import test_hallux_fix


def test_hallux_commit(proj_name: str = "test-project1", tmp_proj_dir: str | None = None):
    if tmp_proj_dir is None:
        if not Path("/tmp/hallux").exists():
            Path("/tmp/hallux").mkdir()
        tmp_proj_dir = tempfile.mkdtemp(dir="/tmp/hallux")

    with set_directory(Path(tmp_proj_dir)):
        try:
            subprocess.check_output(["git", "init"])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # Cannot call `git init`

        proj_dir = Path(__file__).resolve().parent.parent.joinpath(proj_name)
        shutil.copytree(str(proj_dir), tmp_proj_dir, ignore_dangling_symlinks=False, dirs_exist_ok=True)
        try:
            subprocess.check_output(["git", "add", "*"])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # Cannot call `git add *`

        try:
            subprocess.check_output(["git", "commit", "-m", "initial"])
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # Cannot call `git commit`

        git_log_output: str = ""
        try:
            git_log_output = subprocess.check_output(["git", "log", "--pretty=oneline"]).decode("utf8")
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # Cannot call `git log`

        assert len(git_log_output.split("\n")) == 1 + 1, git_log_output  # we have exactly one commit in the repo (+1 empty line)

    test_hallux_fix(proj_name, tmp_proj_dir, command="commit")

    with set_directory(Path(tmp_proj_dir)):
        try:
            git_log_output = subprocess.check_output(["git", "log", "--pretty=oneline"]).decode("utf8")
        except subprocess.CalledProcessError as e:
            pytest.fail(e, pytrace=True)  # Cannot call `git log`

        assert len(git_log_output.split("\n")) == 5 + 1, git_log_output # we have exactly 5 commits in the repo (+1 empty line)
