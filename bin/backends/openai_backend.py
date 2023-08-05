# Copyright: Hallux team, 2023

from __future__ import annotations
from typing import Final
import openai
import os
from openai.api_resources import ChatCompletion

from issues.issue import IssueDescriptor
from backends.query_backend import QueryBackend


class OpenAiChatGPT(QueryBackend):
    def __init__(
        self,
        model: str = "",
        max_tokens: int = 4097,
        type="openai",
        verbose: bool = True,
        previous_backend: QueryBackend | None = None,
    ):
        assert type == "openai"
        super().__init__(previous_backend)
        if model is None or len(model) < 2:
            raise SystemExit(f"Wrong model name for OpenAI API: {model}")

        if os.getenv("OPENAI_API_KEY") is None:
            raise SystemExit("Environment variable OPENAI_API_KEY is required for OpenAI API backend")

        self.model = model
        self.tokens = max_tokens
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.verbose: Final[bool] = verbose

    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:
        if self.verbose:
            print("REQUEST")
            print(request)
        result = ChatCompletion.create(messages=[{"role": "user", "content": request}], model=self.model)
        answers = []
        if len(result["choices"]) > 0:
            for variant in result["choices"]:
                answers.append(variant["message"]["content"])
        if self.verbose:
            print("ANSWERS")
            for ans in answers:
                for line in ans.split("\n"):
                    print(line)
                print()
                print()

        return answers
