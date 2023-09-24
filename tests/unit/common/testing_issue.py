#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path
from typing import Final

from hallux.issues.issue import IssueDescriptor


class TestingIssue(IssueDescriptor):
    def __init__(
        self,
        filename: str,
        tool: str = "tool",
        issue_line: int = 0,
        description: str = "",
        issue_type: str = "warning",
        language: str | None = None,
        base_path: Path | None = None,
    ):
        self.base_path: Final[Path] = base_path if base_path is not None else Path(
            __file__).resolve().parent
        test_file = self.base_path.joinpath(filename)

        # By-default contain absolute full-path, but can contain relative name too, if base_path provided
        testing_filename: str = str(
            test_file) if base_path is None else filename

        super().__init__(
            tool=tool,
            filename=testing_filename,
            issue_line=issue_line,
            description=description,
            issue_type=issue_type,
            language=language,
        )

    def list_proposals(self):
        pass
