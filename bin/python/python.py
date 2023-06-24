#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations
from query_backend import QueryBackend
from diff_target import DiffTarget
from code_processor import CodeProcessor
import subprocess
from pathlib import Path


class PythonProcessor(CodeProcessor):
    def __init__(
        self, query_backend: QueryBackend, diff_target: DiffTarget, base_path: Path, config: dict, debug: bool = False
    ):
        self.query_backend: QueryBackend = query_backend
        self.diff_target: DiffTarget = diff_target
        self.base_path: Path = base_path
        self.config = config
        self.debug: bool = debug

    def process(self) -> None:
        print("Process Python issues:")
        if "linting" in self.config.keys():
            self.python_linting(self.config["linting"])
        if "tests" in self.config.keys():
            self.python_tests(self.config["tests"])
        if "docstrings" in self.config:
            self.python_docstrings(self.config["docstrings"])

    def python_linting(self, config):
        if config != "ruff":
            print("We only support RUFF for python lint")
            exit(5)

        print("Process python linting issues:")

        try:
            subprocess.check_output(["ruff", "check", "."])
            print("No python linting issues found")
        except subprocess.CalledProcessError as e:
            ruff_output = e.output

            warnings: list[str] = str(ruff_output.decode("utf-8")).split("\n")
            for warn in warnings[:-2]:
                print(warn)
                filename = warn.split(" ")[0].split(":")[0]
                warn_line = int(warn.split(" ")[0].split(":")[1])
                added_comment: str = " # line " + str(warn_line)
                start_line, end_line, warnlines, filelines = self.read_lines(filename, warn_line, 4, added_comment)

                request = "Fix python linting issue, write resulting code only:\n"
                request = request + warn + "\n"
                request = request + "Excerpt from the corresponding python file (not full):\n"

                for line in warnlines:
                    request = request + line + "\n"

                print("request")
                print(request)

                result: list[str]

                if self.debug:
                    result = [
                        "        try:\n"
                        + "            token1 = next(tokens1)\n"
                        + "            token2 = next(tokens2)\n"
                        + "        except:\n"
                        + "            break\n\n@pytest.mark.parametrize(\n"
                    ]
                else:
                    result = self.query_backend.query(request)

                if len(result) > 0:
                    resulting_lines = self.prepare_lines(result[0], added_comment)
                    self.diff_target.apply_diff(filename, start_line, end_line, resulting_lines, warn)

                if self.debug:
                    break

    def python_tests(self, params: dict | str):
        pass

    def python_docstrings(self, params: dict | str):
        pass
