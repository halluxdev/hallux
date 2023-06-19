#!/bin/env python
# Runs checks in the current project
# (possible features: unit-tests / docstrings / compilation errors / linting)
# Extracts every single message
# Sends prompt to GPT, receives answer, changes code right in the codebase


from __future__ import annotations
import subprocess
import os
from typing import Final

import yaml
from pathlib import Path
import openai
from openai.api_resources import ChatCompletion


def load_config() -> dict | None:
    curr_path = Path(os.getcwd())
    while not curr_path.joinpath(".hallux").exists() and curr_path.parent != curr_path:
        curr_path = curr_path.parent
    if not curr_path.joinpath(".hallux").exists():
        return None
    config_file = str(curr_path.joinpath(".hallux"))
    with open(config_file) as file_stream:
        yaml_dict = yaml.load(file_stream, Loader=yaml.CLoader)
    return yaml_dict


def python_linting(params: dict | str | None, model: Final[str]):
    print("Process python linting issues:")
    command = params["command"] if "command" in params else ["ruff", "check", "."]
    try:
        subprocess.check_output(command)
        print("No linting issues found")
    except subprocess.CalledProcessError as e:
        ruff_output = e.output

        warnings: list[str] = str(ruff_output.decode("utf-8")).split("\n")
        # for warn in warnings[:-2]:
        if len(warnings) > 2:
            warn = warnings[0]
            print(warn)
            filename = warn.split(" ")[0].split(":")[0]
            warn_line = int(warn.split(" ")[0].split(":")[1])
            with open(filename, "rt") as file:
                filelines = file.read().split("\n")

            request = "Fix python linting issue, write resulting code only:\n"
            request = request + warn + "\n"
            request = request + "Excerpt from the corresponding python file:\n"
            for line in range(warn_line - 3, warn_line + 3):
                if line > 0 and line < len(filelines):
                    request = request + filelines[line] + "\n"
            print("request")
            print(request)
            result = ChatCompletion.create(messages=[{"role": "user", "content": request}], model=model)
            # print("result")
            # print(result)
            if len(result["choices"]) > 0:
                for variant in result["choices"]:
                    resulting_code = variant["message"]["content"]
                    print(resulting_code.split("\\n"))


def python_tests(params: dict | str, model: Final[str]):
    pass


def python_docstrings(params: dict | str, model: Final[str]):
    pass


def cpp_compile(params: dict | str, model: Final[str]):
    pass


def cpp_linking(params: dict | str, model: Final[str]):
    pass


def cpp_tests(params: dict | str, model: Final[str]):
    pass


if __name__ == "__main__":
    config = load_config()

    os.chdir(os.getcwd())

    if config is None:
        print("Error: config file not found")
        exit(1)

    if "backend" not in config.keys():
        print("Backend is not properly configured")
        exit(2)

    model: Final[str] = config["backend"]["model"] if "model" in config["backend"].keys() else None

    if model is None:
        print("Backend has no model")
        exit(3)

    openai.api_key = os.getenv("OPENAI_API_KEY")
    # print(openai.Model.list())
    # assert

    if "python" in config.keys():
        if "linting" in config["python"].keys():
            python_linting(config["python"]["linting"], model=model)
        if "tests" in config["python"].keys():
            python_tests(config["python"]["tests"], model)
        if "docstrings" in config["python"].keys():
            python_docstrings(config["python"]["docstrings"], model)

    # if "cpp" in config.keys():
    #     if "compile" in config["cpp"].keys():
    #         cpp_compile(config["cpp"]["compile"], model)
    #     if "linking" in config["cpp"].keys():
    #         cpp_linking(config["cpp"]["linking"], model)
    #     if "tests" in config["cpp"].keys():
    #         cpp_tests(config["cpp"]["tests"], model)
