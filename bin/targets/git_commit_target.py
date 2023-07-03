# Copyright: Hallux team, 2023

from __future__ import annotations
import subprocess
import os
from pathlib import Path
from file_diff import FileDiff
from targets.filesystem_target import FilesystemTarget


# Saves fixes into local git commits
class GitCommitTarget(FilesystemTarget):
    def __init__(self):
        FilesystemTarget.__init__(self)

    def apply_diff(self, diff: FileDiff) -> None:
        FilesystemTarget.apply_diff(self, diff)

    def revert_diff(self) -> None:
        FilesystemTarget.revert_diff(self)

    def commit_diff(self) -> int:
        curr_dir: str = os.getcwd()
        git_dir: str = str(Path(self.existing_diff.filename).parent)
        os.chdir(git_dir)
        subprocess.check_output(["git", "add", os.path.relpath(self.existing_diff.filename, start=git_dir)])
        subprocess.check_output(["git", "commit", "-m", f'"{self.existing_diff.description}"'])
        FilesystemTarget.commit_diff(self)
        os.chdir(curr_dir)
        return 0
