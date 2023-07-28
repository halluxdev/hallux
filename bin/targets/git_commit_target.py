# Copyright: Hallux team, 2023

from __future__ import annotations
import subprocess
import os
from pathlib import Path
from typing import Final

from proposals.diff_proposal import DiffProposal
from targets.filesystem_target import FilesystemTarget


class GitCommitTarget(FilesystemTarget):
    """
    Saves fixes into local git repo as individual commits
    """

    def __init__(self, verbose: bool = False):
        # ToDo: assert we're in GIT repo, crush if not
        FilesystemTarget.__init__(self)
        git_status_output = subprocess.check_output(["git", "status", "--porcelain"]).decode("utf8")
        if len(git_status_output) > 0:
            raise SystemError("for GIT TARGET you must be in the GIT REPO with no local uncommitted changes!")
        self.verbose: Final[bool] = verbose

    def apply_diff(self, diff: DiffProposal) -> bool:
        return FilesystemTarget.apply_diff(self, diff)

    def revert_diff(self) -> None:
        FilesystemTarget.revert_diff(self)

    def commit_diff(self) -> None:
        curr_dir: str = os.getcwd()
        git_dir: str = str(Path(self.existing_proposal.filename).parent)
        os.chdir(git_dir)

        try:
            if self.verbose:
                print(f"git add {os.path.relpath(self.existing_proposal.filename, start=git_dir)}")
            output = subprocess.check_output(
                ["git", "add", os.path.relpath(self.existing_proposal.filename, start=git_dir)]
            )
            git_message = "HALLUX: " + self.existing_proposal.description.replace('"', "")

            if self.verbose:
                print(output.decode("utf8"))
                print(f"git commit -m {git_message}")

            output = subprocess.check_output(["git", "commit", "-m", f"{git_message}"])
            if self.verbose:
                print(output.decode("utf8"))
            FilesystemTarget.commit_diff(self)
        except subprocess.CalledProcessError as e:
            if self.verbose:
                print("ERROR:")
                print(e.output.decode("utf8"))
            os.chdir(curr_dir)
            FilesystemTarget.revert_diff(self)
            raise e
        finally:
            os.chdir(curr_dir)

    def requires_refresh(self) -> bool:
        return True
