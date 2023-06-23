#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import ABC, abstractmethod
import copy


class CodeProcessor(ABC):
    @abstractmethod
    def process(self) -> None:
        pass

    @staticmethod
    def read_lines(
        filename: str, line: int, raidus: int, add_comment: str | None = None
    ) -> tuple[int, int, list[str], list[str]]:
        with open(filename, "rt") as file:
            filelines = file.read().split("\n")
        start_line = max(0, line - raidus)
        end_line = min(len(filelines) - 1, line + raidus)
        requested_lines = copy.deepcopy(filelines[start_line:end_line])
        requested_lines[line - start_line] += add_comment
        return start_line, end_line, requested_lines, filelines

    @staticmethod
    def prepare_lines(query_result: str, remove_comment: str | None = None) -> list[str]:
        resulting_lines = query_result.split("\n")
        for i in range(len(resulting_lines)):
            line: str = resulting_lines[i]
            if line.endswith(remove_comment):
                resulting_lines[i] = line[: -len(remove_comment)]
                break
        return resulting_lines
