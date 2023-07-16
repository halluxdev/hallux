# Copyright: Hallux team, 2023

from __future__ import annotations
from file_diff import FileDiff
from targets.diff_target import DiffTarget


# Saves diffs directly into local filesystem
class FilesystemTarget(DiffTarget):
    def __init__(self):
        self.existing_diff: FileDiff | None = None

    def apply_diff(self, diff: FileDiff) -> bool:
        if self.existing_diff is not None:
            raise SystemError("FilesystemTarget: Cannot apply new diff, before last one committed or reverted")

        self.existing_diff = diff  # save new diff in the memory

        with open(diff.filename, "wt") as file:
            for line in range(0, diff.start_line - 1):
                file.write(diff.all_lines[line] + "\n")

            for code_line in diff.proposed_lines:
                file.write(code_line + "\n")

            for line in range(diff.end_line, len(diff.all_lines)):
                file.write(diff.all_lines[line])
                if line < len(diff.all_lines) - 1:
                    file.write("\n")

            file.close()
            return True

    def revert_diff(self) -> None:
        if self.existing_diff is not None:
            with open(self.existing_diff.filename, "wt") as file:
                all_lines = self.existing_diff.all_lines
                for line in range(len(all_lines)):
                    file.write(all_lines[line])
                    if line < len(all_lines) - 1:
                        file.write("\n")

            self.existing_diff = None

    def commit_diff(self) -> bool:
        self.existing_diff = None
        return False
