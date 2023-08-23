#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path

import pytest

from tools.cpp.cpp import Cpp_IssueSolver
from tools.factory import ProcessorFactory
from tools.issue_solver import IssueSolver
from tools.mypy.solver import Mypy_IssueSolver
from tools.ruff.solver import Ruff_IssueSolver
from tools.sonarqube.solver import Sonar_IssueSolver

ruff = Ruff_IssueSolver(Path(), Path())
mypy = Mypy_IssueSolver(Path(), Path())
sonar = Sonar_IssueSolver(Path(), Path())
cpp = Cpp_IssueSolver(Path(), Path())


@pytest.mark.parametrize(
    "argv, config, groups, expected_list",
    [
        ([], None, None, [ruff, mypy, sonar, cpp]),  # no settings, no request -> select everything
        ([], {}, None, [ruff, mypy, sonar, cpp]),  # settings empty, no request -> select everything
        ([], {"whatever": {}}, {}, [ruff, mypy, sonar, cpp]),  # not valid request
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
        # individual processors with empty or no config
        (["--ruff"], {}, {}, [ruff]),
        (["--mypy"], {}, {}, [mypy]),
        (["--cpp"], {}, {}, [cpp]),
        (["--sonar"], {}, {}, [sonar]),
        (["--ruff"], None, None, [ruff]),
        (["--mypy"], None, None, [mypy]),
        (["--cpp"], None, None, [cpp]),
        (["--sonar"], None, None, [sonar]),
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
    solvers_list = ProcessorFactory.init_solvers(argv, config, groups, Path(), Path())
    assert len(solvers_list) == len(expected_list)
    assert len(solvers_list) >= 1  # shall always return at least one processor
    for i in range(len(solvers_list)):
        assert isinstance(solvers_list[i], IssueSolver)
        assert type(solvers_list[i]) == type(expected_list[i])  # noqa: E721
