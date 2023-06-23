#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import ABC, abstractmethod
from openai.api_resources import ChatCompletion


class QueryBackend(ABC):
    @abstractmethod
    def query(self, request: str) -> str | None:
        pass


class OpenAiChatGPT(QueryBackend):
    def __init__(self, config: dict):
        self.model = config["model"]
        self.max_tokens = config["max_tokens"]

    def query(self, request: str) -> list[str]:
        result = ChatCompletion.create(messages=[{"role": "user", "content": request}], model=self.model)
        answers = []
        if len(result["choices"]) > 0:
            print(result["choices"])
            for variant in result["choices"]:
                answers.append(variant["message"]["content"])
        return answers
