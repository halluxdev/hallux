#!/usr/bin/env python
# Copyright: Hallux team, 2023-2024

# MAIN COMMAND-LINE EXECUTABLE
# - Runs checks in the current folder (linting / unit-tests / docstrings / compilation errors)
# - Extracts every single message
# - Makes a prompt for every message
# - Sends prompt to GPT, receives answer,
# - Changes code right in the codebase or sends this change as Github Web GUI proposal

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Final

import yaml
import traceback

from hallux.auxilary import find_arg, find_argvalue
from hallux.backends.factory import BackendFactory, QueryBackend
from hallux.logger import logger
from hallux.targets.diff import DiffTarget
from hallux.targets.filesystem import FilesystemTarget
from hallux.targets.git_commit import GitCommitTarget
from hallux.targets.github_suggestion import GithubSuggestion
from hallux.targets.gitlab_suggestion import GitlabSuggestion
from hallux.tools.factory import IssueSolver, ToolsFactory

DEBUG: Final[bool] = False
CONFIG_FILE: Final[str] = ".hallux"


class Hallux:
    # static-like const field
    default_plugins: Final[dict] = {"python": {"ruff": "."}, "cpp": {"compile": True}, "sonar": True}

    def __init__(
        self,
        solvers: list[IssueSolver],
        run_path: Path,  # directory, specified in command-line
        config_path: Path,  # directory of the config file, if exists, or current one
        verbose: bool = False,
    ):
        self.solvers: Final[list[IssueSolver]] = solvers
        self.run_path: Final[Path] = run_path
        self.config_path: Final[Path] = config_path if config_path is not None else run_path
        self.verbose: bool = verbose

    def process(self, diff_target: DiffTarget, query_backend: QueryBackend):
        for solver in self.solvers:
            solver.solve_issues(diff_target, query_backend)

    @staticmethod
    def find_config(run_path: Path) -> tuple[dict, Path]:
        """
        Finds
        :param run_path:
        :return: (config, config_path), config_path shall only be used for filenames, mentioned in config.yaml
        """
        config_path = run_path
        while not config_path.joinpath(CONFIG_FILE).exists() and config_path.parent != config_path:
            config_path = config_path.parent
        if not config_path.joinpath(CONFIG_FILE).exists():
            return {}, run_path
        config_file = str(config_path.joinpath(CONFIG_FILE))
        with open(config_file) as file_stream:
            yaml_dict = yaml.load(file_stream, Loader=yaml.Loader)
            logger.debug(f"Loaded config from {config_file}")
            logger.debug(f"Config: {yaml_dict}")
        return yaml_dict, config_path

    @staticmethod
    def print_usage():
        print(f"Hallux v{get_version()} - Convenient AI Code Quality Assistant\n")
        print("USAGE: ")
        print("hallux [TOOL] [BACKEND] [TARGET] [OTHER] DIR")

        print("\nOptions for [TOOL]:")
        print("--all       (DEFAULT) try all plugins, or configured ones")
        print("--sonar     try fixing issues, coming from SonarQube")
        print("--python    try fixing only python issues")
        print("--ruff      try fixing only only ruff issues")
        print("--cpp       try fixing only c++ issues")

        print("\nOptions for [BACKEND]: If specified, Hallux will not try other, less prioritized backends")
        print("Here is list of BACKENDS, sorted by their priority (may be changed in config file):")
        print("--cache     (highest priority) Reads solutions from local JSON file, specified in the config")
        print("--gpt3      Uses OpenAI ChatGPT v3.5 for solving issues")
        print("--gpt4      (lowest priority) Uses OpenAI ChatGPT v4 for solving issues")
        print("More details on [BACKEND] options: https://hallux.dev/docs/user-guide/backends")

        print("\nOptions for [TARGET]:")
        print("--files     (DEFAULT) Writes fixes directly into local files")
        print("--git       Adds separate git commit for every fix,")
        print("--github https://github.com/ORG_NAME/REPO_NAME/pull/ID")
        print("            Submit issue fixes as suggestions into Github Pull-Request,")
        print("--gitlab https://gitlab.com/GROUP_NAME/REPO_NAME/-/merge_requests/ID")
        print("            Submit issue fixes as suggestions into Gitlab Merge-Request,")
        print("More details on [TARGET] options: https://hallux.dev/docs/user-guide/targets")

        print("\nOptions for [OTHER]:")
        print("--verbose   Print debug tracebacks on errors")
        print("--help      Print this help section")

    @staticmethod
    def init_target(argv: list[str], config: dict | str) -> DiffTarget:
        # Command-line arguments have highest priority:
        github_index = find_arg(argv, "--github")
        if github_index > 0:
            github_value = find_argvalue(argv, "--github")
            if github_value is not None:
                return GithubSuggestion(github_value)
            else:
                raise SystemError(
                    "--github must be followed by valid PR URL, like this https://github.com/ORG_NAME/REPO_NAME/pull/ID"
                )
        gitlab_index = find_arg(argv, "--gitlab")
        if gitlab_index > 0:
            gitlab_value = find_argvalue(argv, "--gitlab")
            if gitlab_value is not None:
                return GitlabSuggestion(gitlab_value)
            else:
                raise SystemError(
                    "--gitlab must be followed by valid MR URL, like this"
                    " https://gitlab.com/GROUP_NAME/REPO_NAME/-/merge_requests/ID"
                )

        if find_arg(argv, "--git") > 0:
            return GitCommitTarget()

        if find_arg(argv, "--files") > 0:
            return FilesystemTarget()

        # Config settings has medium priority:
        if "github" in config:
            return GithubSuggestion(config["github"])
        elif config == "git" or "git" in config:
            return GitCommitTarget()
        # If no other targets were found - use default
        return FilesystemTarget()


def get_version():
    try:
        with open(Path(__file__).parent / "VERSION") as version_file:
            return version_file.read().strip()
    except FileNotFoundError:
        return "DEVELOP"


def main(argv: list[str] | None = None, run_path: Path | None = None) -> int:
    """
    :param argv: list of command-line arguments
    :param run_path: Path, from where main executable is running
    :return: error code or 0, if successful
    """
    if argv is None:
        argv = sys.argv

    verbose: bool = find_arg(argv, "--verbose") > 0 or find_arg(argv, "-v") > 0
    if verbose:
        logger.setLevel(logging.DEBUG)

    if len(argv) < 2 or is_help_requested(argv):
        Hallux.print_usage()
        return 0

    run_path = run_path or Path().resolve()
    command_dir = validate_command_dir(argv)
    if command_dir is None:
        return 1

    config, config_path = Hallux.find_config(run_path)

    error_code, query_backend = init_backend(argv, config, config_path, verbose)
    if query_backend is None:
        return error_code

    error_code, target = init_target(argv, config, verbose)
    if target is None:
        return error_code

    error_code, solvers = init_solvers(argv, config, config_path, run_path, command_dir, verbose)
    if solvers is None:
        return error_code

    error_code, hallux = init_hallux(solvers, run_path, config_path, verbose)
    if hallux is None:
        return error_code

    if (error_code := process_hallux(hallux, query_backend, target, verbose)) != 0:
        return error_code

    return 0


def is_help_requested(argv):
    return len(argv) == 2 and (argv[1] in ["--help", "-h", "-?"])


def validate_command_dir(argv):
    if Path(argv[-1]).exists() and Path(argv[-1]).is_dir():
        return argv[-1]
    logger.error(f"{argv[-1]} is not a valid DIR")
    return None


def init_backend(argv, config, config_path, verbose):
    try:
        query_backend: QueryBackend = BackendFactory.init_backend(argv, config, config_path)
        return 0, query_backend
    except Exception as e:
        logger.error(f"Error during BACKEND initialization: {e}")
        if verbose:
            raise e
        return 2, None


def init_target(argv, config, verbose):
    try:
        target: DiffTarget = Hallux.init_target(argv, config.get("target", {}))
        return 0, target
    except Exception as e:
        logger.error(f"Error during TARGET initialization: {e}")
        if verbose:
            raise e
        return 3, None


def init_solvers(argv, config, config_path, run_path, command_dir, verbose):
    try:
        solvers: list[IssueSolver] = ToolsFactory.init_solvers(
            argv,
            config.get("tools"),
            config.get("groups"),
            config_path=config_path,
            run_path=run_path,
            command_dir=command_dir,
        )
        return 0, solvers
    except Exception as e:
        logger.error(f"Error during SOLVERS initialization: {e}")
        if verbose:
            raise e
        return 4, None


def init_hallux(solvers, run_path, config_path, verbose):
    try:
        hallux = Hallux(
            solvers=solvers,
            run_path=run_path,
            config_path=config_path,
        )
        return 0, hallux
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        if verbose:
            raise e
        return 5, None


def process_hallux(hallux, query_backend, target, verbose):
    try:
        hallux.process(query_backend=query_backend, diff_target=target)
        return 0
    except Exception as e:
        logger.error(f"Error during process: {e.args}")
        traceback.print_exc()
        if verbose:
            raise e
        return 6


if __name__ == "__main__":
    ret_val = main(sys.argv)
    sys.exit(ret_val)
