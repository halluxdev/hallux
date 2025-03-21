#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path

import pytest

from hallux.tools.cpp.cpp import Cpp_IssueSolver
from hallux.tools.factory import ToolsFactory
from hallux.tools.issue_solver import IssueSolver
from hallux.tools.mypy.solver import Mypy_IssueSolver
from hallux.tools.ruff.solver import Ruff_IssueSolver
from hallux.tools.sonarqube.solver import Sonar_IssueSolver

ruff = Ruff_IssueSolver(Path(), Path())
mypy = Mypy_IssueSolver(Path(), Path())
sonar = Sonar_IssueSolver(Path(), Path())
sonar_extra = Sonar_IssueSolver(Path(), Path(), argvalue="extra_param")
sonar_localhost = Sonar_IssueSolver(Path(), Path(), url="https://localhost")

cpp = Cpp_IssueSolver(Path(), Path())


def same_as(first: Sonar_IssueSolver, second: Sonar_IssueSolver) -> bool:
    same = first.project == second.project
    same = same and (first.search_params == second.search_params)
    same = same and (first.argvalue == second.argvalue)
    return same


@pytest.mark.parametrize(
    "argv, config, groups, expected_list",
    [
        # no settings, no request -> select everything
        ([], None, None, [ruff, mypy, sonar, cpp]),
        # settings empty, no request -> select everything
        ([], {}, None, [ruff, mypy, sonar, cpp]),
        # not valid request
        ([], {"whatever": {}}, {}, [ruff, mypy, sonar, cpp]),
        (
            ["--whatever"],
            {"whatever": {}},
            {},
            [ruff, mypy, sonar, cpp],
        ),  # still not valid, as whatever is not valid processor name
        (
            ["--whatever"],
            {},
            {"whatever": ["ruff"]},
            [ruff],
        ),  # now whatever is valid group name
        # individual tools with empty or no config
        (["--ruff"], {}, {}, [ruff]),
        (["--mypy"], {}, {}, [mypy]),
        (["--cpp"], {}, {}, [cpp]),
        (["--sonar"], {}, {}, [sonar]),
        (["--ruff"], None, None, [ruff]),
        (["--mypy"], None, None, [mypy]),
        (["--cpp"], None, None, [cpp]),
        (["--sonar"], None, None, [sonar]),
        (["--sonar", "extra_param"], None, None, [sonar_extra]),
        (["--sonar=extra_param"], None, None, [sonar_extra]),
        (["--sonar", "--sonar.url=https://localhost"], None, None, [sonar_localhost]),
        (["--sonar", "--sonar.urldfsfsfsf=https://localhost"], None, None, [sonar_localhost]),
        # combinations
        (["--sonar", "--cpp"], None, None, [sonar, cpp]),
        (["--sonar=extra_param", "--cpp"], None, None, [sonar_extra, cpp]),
        (["--sonar", "extra_param", "--cpp"], None, None, [sonar_extra, cpp]),
        # default groups
        (["--python"], {}, None, [ruff, mypy]),
        (["--all"], {}, None, [ruff, mypy, sonar, cpp]),
        # here, python is no longer valid group -> return all
        (["--python"], {}, {}, [ruff, mypy, sonar, cpp]),
        (["--all"], {}, {}, [ruff, mypy, sonar, cpp]),
    ],
)
def test_init_solvers(argv: list[str], config: dict, groups: dict, expected_list: list):
    argv = ["hallux"] + argv
    solvers_list = ToolsFactory.init_solvers(argv, config, groups, Path(), Path())
    assert len(solvers_list) == len(expected_list)
    assert len(solvers_list) >= 1  # shall always return at least one processor
    for i in range(len(solvers_list)):
        assert isinstance(solvers_list[i], IssueSolver)
        assert type(solvers_list[i]) == type(expected_list[i])  # noqa: E721
        if isinstance(solvers_list[i], Sonar_IssueSolver):
            assert same_as(solvers_list[i], expected_list[i])
