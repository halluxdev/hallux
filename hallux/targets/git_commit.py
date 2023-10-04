# Copyright: Hallux team, 2023

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from hallux.logger import logger

from ..proposals.diff_proposal import DiffProposal
from .filesystem import FilesystemTarget


class GitCommitTarget(FilesystemTarget):
    """
    Saves fixes into local git repo as individual commits
    """

    def __init__(self):
        # ToDo: assert we're in GIT repo, crash if not
        FilesystemTarget.__init__(self)
        git_status_output = subprocess.check_output(["git", "status", "--porcelain"]).decode("utf8")
        if len(git_status_output) > 0:
            raise SystemError("for GIT TARGET you must be in the GIT REPO with no local uncommitted changes!")

    def apply_diff(self, diff: DiffProposal) -> bool:
        return FilesystemTarget.apply_diff(self, diff)

    def revert_diff(self) -> None:
        FilesystemTarget.revert_diff(self)

    def commit_diff(self) -> bool:
        curr_dir: str = os.getcwd()
        git_dir: str = str(Path(self.existing_proposal.filename).parent)
        os.chdir(git_dir)
        success: bool = True
        try:
            logger.debug(f"git add {os.path.relpath(self.existing_proposal.filename, start=git_dir)}")
            output = subprocess.check_output(
                ["git", "add", os.path.relpath(self.existing_proposal.filename, start=git_dir)]
            )
            git_message = "HALLUX: " + self.existing_proposal.description.replace('"', "")

            logger.debug(output.decode("utf8"))
            logger.debug(f"git commit -m {git_message}")

            output = subprocess.check_output(["git", "commit", "-m", f"{git_message}"])

            logger.debug(output.decode("utf8"))
            FilesystemTarget.commit_diff(self)
        except subprocess.CalledProcessError as e:
            logger.debug("ERROR:")
            logger.debug(e.output.decode("utf8"))
            FilesystemTarget.revert_diff(self)
            success = False
        finally:
            os.chdir(curr_dir)

        return success

    def requires_refresh(self) -> bool:
        return True
