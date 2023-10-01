# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path

from ..auxilary import set_directory
from ..proposals.diff_proposal import DiffProposal
from .diff import DiffTarget


# Saves diff-proposals directly into local filesystem
class FilesystemTarget(DiffTarget):
    def __init__(self):
        self.existing_proposal: DiffProposal | None = None
        self.base_path: Path | None = None

    def apply_diff(self, proposal: DiffProposal) -> bool:
        if self.existing_proposal is not None:
            raise SystemError("FilesystemTarget: Cannot apply new diff, before last one committed or reverted")

        if not Path(proposal.filename).exists():
            raise SystemError(f"FilesystemTarget: Cannot find file: {proposal.filename}")

        self.base_path = Path().absolute()
        self.existing_proposal = proposal  # save new diff in the memory

        with open(proposal.filename, "wt") as file:
            for line in range(0, proposal.start_line - 1):
                file.write(proposal.all_lines[line] + "\n")

            for code_line in proposal.proposed_lines:
                file.write(code_line + "\n")

            for line in range(proposal.end_line, len(proposal.all_lines)):
                file.write(proposal.all_lines[line])
                if line < len(proposal.all_lines) - 1:
                    file.write("\n")

            file.close()
        return True

    def revert_diff(self) -> None:
        if self.existing_proposal is not None:
            with set_directory(self.base_path):
                with open(self.existing_proposal.filename, "wt") as file:
                    all_lines = self.existing_proposal.all_lines
                    for line in range(len(all_lines)):
                        file.write(all_lines[line])
                        if line < len(all_lines) - 1:
                            file.write("\n")

            self.existing_proposal = None
            self.base_path = None

    def commit_diff(self) -> bool:
        self.existing_proposal = None
        self.base_path = None
        return True

    def requires_refresh(self) -> bool:
        return True
