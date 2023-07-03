# Copyright: Hallux team, 2023

from __future__ import annotations
import json
from abc import ABC, abstractmethod
import openai
import os
from pathlib import Path
from openai.api_resources import ChatCompletion
from issue import IssueDescriptor


class QueryBackend(ABC):
    @abstractmethod
    def query(self, request: str, issue: IssueDescriptor | None = None) -> list[str] | None:
        pass


class OpenAiChatGPT(QueryBackend):
    def __init__(self, config: dict):
        self.model = config["model"]
        self.max_tokens = config["max_tokens"]
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def query(self, request: str, issue: IssueDescriptor | None = None) -> list[str]:
        print("REQUEST")
        print(request)
        result = ChatCompletion.create(messages=[{"role": "user", "content": request}], model=self.model)
        answers = []
        if len(result["choices"]) > 0:
            for variant in result["choices"]:
                answers.append(variant["message"]["content"])
        print("ANSWERS")
        print(answers)
        return answers


class DummyBackend(QueryBackend):
    def __init__(self, filename: str, base_path: Path):
        self.filename: str = filename
        self.base_path = base_path
        with open(self.filename, "rt") as file:
            self.json = json.load(file)

    def query(self, request: str, issue: IssueDescriptor | None = None) -> list[str]:
        if issue is None:
            return []

        language = self.json.get(issue.language)
        if language is None:
            return []

        tool = language.get(issue.tool)
        if tool is None:
            return []

        issue_file = Path(issue.filename) if Path(issue.filename).exists() else self.base_path.joinpath(issue.filename)
        for filename, file_issues in tool.items():
            answer_file = self.base_path.joinpath(filename)
            if issue_file.samefile(answer_file) and issue.description in file_issues:
                return file_issues[issue.description]

        return []
