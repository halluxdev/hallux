#!/usr/bin/env python
# Copyright: Hallux team, 2023

# MAIN COMMAND-LINE EXECUTABLE
# - Runs checks in the current folder (linting / unit-tests / docstrings / compilation errors)
# - Extracts every single message
# - Makes a prompt for every message
# - Sends prompt to GPT, receives answer,
# - Changes code right in the codebase or sends this change as Github Web GUI proposal

from __future__ import annotations
import os
import sys
from typing import Final
import yaml
from pathlib import Path

from backends.query_backend import QueryBackend
from backends.openai_backend import OpenAiChatGPT
from backends.dummy_backend import DummyBackend
from targets.diff_target import DiffTarget
from targets.filesystem_target import FilesystemTarget
from targets.git_commit_target import GitCommitTarget
from targets.github_proposal_traget import GithubProposalTraget
from processors.cpp.cpp import CppProcessor
from processors.python.python import PythonProcessor
from processors.sonar import SonarProcessor

DEBUG: Final[bool] = False
CONFIG_FILE: Final[str] = ".hallux"


class Hallux:
    # static-like const field
    default_plugins: Final[dict] = {"python": {"ruff": "."}, "cpp": {"compile": True}, "sonar": True}

    def __init__(
        self,
        query_backend: QueryBackend,
        diff_target: DiffTarget,
        config: dict,
        run_path: Path,  # current directory where hallux is executed
        config_path: Path | None = None,  # directory of the config file, if any
        verbose: bool = False,
    ):
        self.query_backend = query_backend
        self.diff_target: Final[DiffTarget] = diff_target
        self.config: Final[dict] = config
        self.run_path: Final[Path] = run_path
        self.config_path: Final[Path] = config_path if config_path is not None else run_path
        self.verbose: bool = verbose

    def process(self):
        if "python" in self.config.keys():
            python = PythonProcessor(
                self.query_backend,
                self.diff_target,
                self.run_path,
                self.config_path,
                self.config["python"],
                self.verbose,
            )
            python.process()

        if "cpp" in self.config.keys():
            cpp = CppProcessor(
                self.query_backend, self.diff_target, self.run_path, self.config_path, self.config["cpp"], self.verbose
            )
            cpp.process()

        if "sonar" in self.config.keys():
            sonar = SonarProcessor(
                self.query_backend,
                self.diff_target,
                self.run_path,
                self.config_path,
                self.config["sonar"],
                self.verbose,
            )
            sonar.process()

    @staticmethod
    def find_config(run_path: Path) -> tuple[dict, Path]:
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
        print("Hallux v0.1 - Convenient Coding Assistant")
        print("USAGE: ")
        print("hallux [COMMAND] [TARGET] [BACKEND] [PLUGINS] [OTHER]")
        print()
        print("Options for [COMMAND]:")
        print("fix         (DEFAULT) Tries fixing issues just once and exists")
        print("agent       Monitors [TARGET] and tries fixing issues in the infinite loop")
        print()
        print("Options for [TARGET]:")
        print("--files     (DEFAULT) Writes fixes directly into local files.")
        print("--git       Adds separate git commit for every fix,")
        print("            must be in GIT repository to enable this")
        print("--github https://BUSINESS.github.com/YOUR_NAME/REPO_NAME/pull/ID")
        print("            Submits proposals into Github Pull-Request,")
        print("            must be in GIT repository to enable this,")
        print("            head SHA in local git and on Github must be same,")
        print("            env variable GITHUB_TOKEN must be properly set,")
        print()
        print("Options for [BACKEND]: ")
        print("--dummy [DUMMY.JSON]  ")
        print("            (DEFAULT) reads/writes all queries from/to DUMMY.JSON file")
        print("            If [DUMMY.JSON] not specified it is defaulted to 'dummy.json'")
        print("--openai [MODEL-NAME] [MAX-TOKENS]")
        print("            Uses OpenAI API for queries,")
        print("            env variable OPENAI_API_KEY must be properly set.")
        print("            If [MODEL-NAME] not specified it is defaulted to gpt-3.5-turbo")
        print("            If [MAX-TOKENS] not specified it is defaulted to 4097")
        print()
        print("Options for [PLUGINS]:")
        print("--all       (DEFAULT) try all plugins, or configured ones")
        print("--python    try fixing only python issues")
        print("--cpp       try fixing only c++ issues")
        print("--ruff      try fixing only only ruff issues")
        print("--gcc-make  try fixing only only gcc-make issues")
        print("Options for [OTHER]:")
        print("--verbose   Print debug tracebacks on errors")

    @staticmethod
    def find_arg(argv: list[str], name: str) -> int:
        """
        Finds argument index and list of following arguments
        """
        for i in range(len(argv)):
            arg = argv[i]
            if arg == name or arg.startswith(name):
                return i
        return -1

    @staticmethod
    def init_target(argv: list[str], config: dict | str, verbose: bool = False) -> DiffTarget:
        # Command-line arguments have highest priority:
        github_index = Hallux.find_arg(argv, "--github")
        if github_index > 0:
            if len(argv) > github_index:
                return GithubProposalTraget(argv[github_index + 1])
            else:
                raise SystemError(
                    "--github must be followed by proper URL like"
                    " https://BUSINESS.github.com/YOUR_NAME/REPO_NAME/pull/ID"
                )

        if Hallux.find_arg(argv, "--git") > 0:
            return GitCommitTarget(verbose=verbose)

        if Hallux.find_arg(argv, "--files") > 0:
            return FilesystemTarget()

        # Config settings has medium priority:
        if "github" in config:
            return GithubProposalTraget(config["github"])
        elif config == "git" or "git" in config:
            return GitCommitTarget()
        # If no other targets were found - use default
        return FilesystemTarget()

    @staticmethod
    def init_backend(argv: list[str], config: dict, config_path: Path) -> QueryBackend:
        default_model = "gpt-3.5-turbo"
        default_max_tokens = 4097
        default_dummy_file = "dummy.json"

        # Get values from config
        openai_config = config.get("openai")
        model = openai_config.get("model") if openai_config else default_model
        max_tokens = (
            int(openai_config.get("max_tokens"))
            if openai_config and "max_tokens" in openai_config
            else default_max_tokens
        )

        dummy_json_file = config.get("dummy", default_dummy_file)

        # Overwrite with command-line arguments
        openai_index = Hallux.find_arg(argv, "--openai")
        if openai_index > 0 and len(argv) > openai_index + 1:
            if argv[openai_index + 1].startswith("gpt-"):
                model = argv[openai_index + 1]
                if len(argv) > openai_index + 1 and int(argv[openai_index + 2]) > 1000:
                    max_tokens = int(argv[openai_index + 2])

        dummy_index = Hallux.find_arg(argv, "--dummy")
        if dummy_index > 0 and len(argv) > dummy_index + 1 and argv[dummy_index + 1].endswith(".json"):
            dummy_json_file = argv[dummy_index + 1]

        # Determine backend based on conditions
        if openai_index > 0 or ("openai" in config and dummy_index < 0):
            return OpenAiChatGPT(model, max_tokens)

        return DummyBackend(dummy_json_file, base_path=config_path)

    @staticmethod
    def init_plugins(argv: list[str], config: dict) -> dict:
        # not properly implemented yet
        plugins = ["python", "cpp", "sonar"]
        new_config = {}
        for plug in plugins:
            plug_ind = Hallux.find_arg(argv, "--" + plug)
            if plug_ind > 0:
                if plug in config:
                    new_config[plug] = config[plug]
                else:
                    new_config[plug] = Hallux.default_plugins[plug]
        # if any plugin mentioned in the arguments, we run it (them), otherwise run those which are in config
        return new_config if len(new_config) > 0 else config


def main(argv: list[str], run_path: Path | None = None) -> int: 
    verbose: bool = Hallux.find_arg(argv, "--verbose") > 0 or Hallux.find_arg(argv, "-v") > 0
    
    if run_path is None:
        run_path = Path(os.getcwd())

    config, config_path = Hallux.find_config(run_path)
    if len(argv) < 2:
        Hallux.print_usage()
        return 0

    try:
        query_backend: QueryBackend = Hallux.init_backend(
            argv, config["backend"] if "backend" in config else {}, config_path
        )
    except Exception as e:
        print(f"Error during BACKEND initialization: {e}", file=sys.stderr)
        if verbose:
            raise e
        return 1

    try:
        target: DiffTarget = Hallux.init_target(argv, config["target"] if "target" in config else {}, verbose)
    except Exception as e:
        print(f"Error during TARGET initialization: {e}", file=sys.stderr)
        if verbose:
            raise e
        return 2

    try:
        plugins: dict = Hallux.init_plugins(argv, config)
    except Exception as e:
        print(f"Error during PLUGINS initialization: {e}", file=sys.stderr)
        if verbose:
            raise e
        return 3

    try:
        hallux = Hallux(
            query_backend=query_backend,
            diff_target=target,
            config=plugins,
            run_path=run_path,
            config_path=config_path,
            verbose=verbose,
        )
    except Exception as e:
        print(f"Error during MAIN PROGRAM initialization: {e}", file=sys.stderr)
        if verbose:
            raise e
        return 3

    try:
        hallux.process()
    except Exception as e:
        print(f"Error during MAIN process: {e.args}", file=sys.stderr)
        if verbose:
            raise e
        return 3

    return 0


if __name__ == "__main__":
    ret_val = main(sys.argv, Path(os.getcwd()))
    exit(ret_val)
