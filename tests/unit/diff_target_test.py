#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

# import tempfile
# import pytest
# import shutil
# from pathlib import Path
# import subprocess
from diff_target import FilesystemTarget


def test_filesystem_target():
    fs_target = FilesystemTarget()
    fs_target.apply_diff()
