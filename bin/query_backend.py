#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations
import json
from abc import ABC, abstractmethod
import openai
import os
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
        result = ChatCompletion.create(messages=[{"role": "user", "content": request}], model=self.model)
        answers = []
        if len(result["choices"]) > 0:
            print(result["choices"])
            for variant in result["choices"]:
                answers.append(variant["message"]["content"])
        return answers


class DummyBackend(QueryBackend):
    def __init__(self, filename: str):
        self.filename: str = filename
        with open(self.filename, "rt") as file:
            self.json = json.load(file)

    def query(self, request: str, issue: IssueDescriptor | None = None) -> list[str]:
        if issue is not None:
            if issue.language in self.json:
                language = self.json[issue.language]
                if issue.tool in language:
                    tool = language[issue.tool]
                    if issue.filename in tool:
                        filename = tool[issue.filename]
                        if issue.description in filename:
                            return filename[issue.description]

        return []
