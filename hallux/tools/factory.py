# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path

from ..auxilary import find_arg, find_argvalue
from ..tools.cpp.cpp import Cpp_IssueSolver
from ..tools.issue_solver import IssueSolver
from ..tools.mypy.solver import Mypy_IssueSolver
from ..tools.ruff.solver import Ruff_IssueSolver
from ..tools.sonarqube.solver import Sonar_IssueSolver


class ProcessorFactory:
    @staticmethod
    def init_solvers(
        argv: list[str],
        tools_config: dict | None,
        groups: dict[str, list[str]] | None,
        config_path: Path,
        run_path: Path,
        command_dir: str = ".",
    ) -> list[IssueSolver]:
        tools_config = tools_config if tools_config is not None else {}
        mapping: dict = {
            "ruff": Ruff_IssueSolver,
            "mypy": Mypy_IssueSolver,
            "sonar": Sonar_IssueSolver,
            "cpp": Cpp_IssueSolver,
        }

        groups = (
            groups
            if groups is not None
            else {
                "all": list(mapping),
                "python": ["ruff", "mypy"],
            }
        )

        requested_names: dict[str] = {}

        # first check for any particular group(s)
        for group_name, group_list in groups.items():
            if find_arg(argv, "--" + group_name) > 0:
                for name in group_list:
                    requested_names[name] = True

        # if not groups asked, check for individual processors
        if len(requested_names) == 0:
            for name in mapping.keys():
                if find_arg(argv, "--" + name) > 0:
                    requested_names[name] = True

        # if nothing particular asked - just use all of them
        if len(requested_names) == 0:
            requested_names = mapping

        solvers: list[IssueSolver] = []
        for name in requested_names:
            classname = mapping[name]
            config_params = tools_config.get(name, {})
            if name == "sonar":
                argvalue = find_argvalue(argv, "--" + name)
                if argvalue is not None:
                    config_params["extra_param"] = argvalue

            solver = classname(**config_params, config_path=config_path, run_path=run_path, command_dir=command_dir)
            solvers.append(solver)

        return solvers
