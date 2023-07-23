# Copyright: Hallux team, 2023

from __future__ import annotations
import subprocess
import os
from pathlib import Path
from proposals.diff_proposal import DiffProposal
from targets.filesystem_target import FilesystemTarget


# Saves fixes into local git commits
class GitCommitTarget(FilesystemTarget):
    def __init__(self):
        # ToDo: assert we're in GIT repo, crush if not
        FilesystemTarget.__init__(self)
        git_status_output = subprocess.check_output(["git", "status", "--porcelain"]).decode("utf8")
        if len(git_status_output) > 0:
            raise SystemError("for GIT target you must be in the GIT REPO with no local uncommitted changes!")

    def apply_diff(self, diff: DiffProposal) -> bool:
        return FilesystemTarget.apply_diff(self, diff)

    def revert_diff(self) -> None:
        FilesystemTarget.revert_diff(self)

    def commit_diff(self) -> None:
        curr_dir: str = os.getcwd()
        git_dir: str = str(Path(self.existing_proposal.filename).parent)
        os.chdir(git_dir)
        subprocess.check_output(["git", "add", os.path.relpath(self.existing_proposal.filename, start=git_dir)])
        subprocess.check_output(["git", "commit", "-m", f'"{self.existing_proposal.description}"'])
        FilesystemTarget.commit_diff(self)
        os.chdir(curr_dir)

    def requires_refresh(self) -> bool:
        return True
