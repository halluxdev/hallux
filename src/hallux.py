#!/usr/bin/env python
# Copyright: Hallux team, 2023

# MAIN COMMAND-LINE EXECUTABLE
# - Runs checks in the current folder (linting / unit-tests / docstrings / compilation errors)
# - Extracts every single message
# - Makes a prompt for every message
# - Sends prompt to GPT, receives answer,
# - Changes code right in the codebase or sends this change as Github Web GUI proposal

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Final

import yaml

from auxilary import find_arg
from backends.factory import BackendFactory, QueryBackend
from targets.diff_target import DiffTarget
from targets.filesystem_target import FilesystemTarget
from targets.git_commit_target import GitCommitTarget
from targets.github_proposal_traget import GithubProposalTraget
from tools.factory import IssueSolver, ProcessorFactory

try:
    from __version__ import version
except ImportError:
    with open(Path(__file__).resolve().parent.parent.joinpath("version.txt"), "rt") as f:
        version = f.read().split("\n")[0] + ".DEVELOP"

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
            yaml_dict = yaml.load(file_stream, Loader=yaml.CLoader)
        return yaml_dict, config_path

    @staticmethod
    def print_usage():
        print(f"Hallux v{version} - Convenient Coding Assistant")
        print("USAGE: ")
        print("hallux [TARGET] [BACKEND] [PLUGINS] [OTHER] DIR")
        print()
        print("Options for [TARGET]:")
        print("--files     (DEFAULT) Writes fixes directly into local files")
        print("--git       Adds separate git commit for every fix,")
        print("            must be in GIT repository with no uncommitted changes to enable this")
        print("--github https://BUSINESS.github.com/YOUR_NAME/REPO_NAME/pull/ID")
        print("            Submits proposals into Github Pull-Request,")
        print("            must be in GIT repository with no uncommitted changes to enable this")
        print("            head SHA in local git and on Github must be same,")
        print("            env variable ${GITHUB_TOKEN} must be properly set,")
        print()
        print("Options for [BACKEND]: If specified, Hallux will not try other, less prioritized backends")
        print("Here is list of BACKENDS, sorted by their priority (may be changed in config file):")
        print("--cache     (highest priority) Reads solutions from JSON file, specified in the config")
        print("            If upper-level backend successfully solves an issue, solution stored for future use")
        print("            If JSON file is not specified in the config, 'dummy.json' is used")
        # print("--free      Uses free Hallux.dev backend for solving issues (limited capacity)")
        print("--gpt3      Uses OpenAI ChatGPT v3.5 for solving issues")
        print("            Requires valid ${OPENAI_API_KEY} env variable.")
        print("--gpt4      (lowest priority) Uses OpenAI ChatGPT v4 for solving issues")
        print("            Requires valid ${OPENAI_API_KEY} env variable.")
        print()
        print("Options for [PLUGINS]:")
        print("--all       (DEFAULT) try all plugins, or configured ones")
        print("--sonarqube try fixing issues, coming from SonarQube")
        print("--python    try fixing only python issues")
        print("--ruff      try fixing only only ruff issues")
        print("--cpp       try fixing only c++ issues")
        print("Options for [OTHER]:")
        print("--verbose   Print debug tracebacks on errors")

    @staticmethod
    def init_target(argv: list[str], config: dict | str, verbose: bool = False) -> DiffTarget:
        # Command-line arguments have highest priority:
        github_index = find_arg(argv, "--github")
        if github_index > 0:
            if len(argv) > github_index:
                return GithubProposalTraget(argv[github_index + 1])
            else:
                raise SystemError(
                    "--github must be followed by proper URL like"
                    " https://BUSINESS.github.com/YOUR_NAME/REPO_NAME/pull/ID"
                )

        if find_arg(argv, "--git") > 0:
            return GitCommitTarget(verbose=verbose)

        if find_arg(argv, "--files") > 0:
            return FilesystemTarget()

        # Config settings has medium priority:
        if "github" in config:
            return GithubProposalTraget(config["github"])
        elif config == "git" or "git" in config:
            return GitCommitTarget()
        # If no other targets were found - use default
        return FilesystemTarget()


def main(argv: list[str], run_path: Path | None = None) -> int:
    """
    :param argv: list of command-line arguments
    :param run_path: Path, from where main executable is running
    :return: error code or 0, if successful
    """
    verbose: bool = find_arg(argv, "--verbose") > 0 or find_arg(argv, "-v") > 0

    if len(argv) < 2:
        Hallux.print_usage()
        return 0

    if run_path is None:
        run_path = Path().resolve()

    if Path(argv[-1]).exists() and Path(argv[-1]).is_dir():
        # directory, which needs to be processed, as requested from the CLI. Relative to run_path. Could be "."
        command_dir: str = argv[-1]
    else:
        print(f"{argv[-1]} is not a valid DIR", file=sys.stderr)
        return 1

    config: dict[str, Any]
    # Path, where config file is found. Shall be only used for filename/paths, defined in the config itself
    config_path: Path
    config, config_path = Hallux.find_config(run_path)

    try:
        query_backend: QueryBackend = BackendFactory.init_backend(
            argv, config.get("backends", None), config_path, verbose=verbose
        )
    except Exception as e:
        print(f"Error during BACKEND initialization: {e}", file=sys.stderr)
        if verbose:
            raise e
        return 2

    try:
        target: DiffTarget = Hallux.init_target(argv, config.get("target", {}), verbose)
    except Exception as e:
        print(f"Error during TARGET initialization: {e}", file=sys.stderr)
        if verbose:
            raise e
        return 3

    try:
        solvers: list[IssueSolver] = ProcessorFactory.init_solvers(
            argv,
            config.get("solvers"),
            config.get("groups"),
            config_path=config_path,
            run_path=run_path,
            command_dir=command_dir,
            verbose=verbose,
        )
    except Exception as e:
        print(f"Error during SOLVERS initialization: {e}", file=sys.stderr)
        if verbose:
            raise e
        return 4

    try:
        hallux = Hallux(
            solvers=solvers,
            run_path=run_path,
            config_path=config_path,
            verbose=verbose,
        )
    except Exception as e:
        print(f"Error during initialization: {e}", file=sys.stderr)
        if verbose:
            raise e
        return 5

    try:
        hallux.process(query_backend=query_backend, diff_target=target)
    except Exception as e:
        print(f"Error during process: {e.args}", file=sys.stderr)
        if verbose:
            raise e
        return 6

    return 0


if __name__ == "__main__":
    ret_val = main(sys.argv)
    sys.exit(ret_val)
