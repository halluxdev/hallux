# Copyright: Hallux team, 2023

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from litellm import completion

from hallux.logger import logger

from ..issues.issue import IssueDescriptor
from .query_backend import QueryBackend


class LiteLLMBackend(QueryBackend):
    def __init__(
        self,
        model: str = "",
        type="litellm",
        base_path: Path = Path(),
        previous_backend: QueryBackend | None = None,
        prompt: object = None,
    ):
        assert type == "litellm"
        super().__init__(base_path, previous_backend)

        self.valid = True
        if model is None or len(model) < 2:
            logger.warning(f"Wrong model name for LiteLLM Backend: {model}")
            self.valid = False

        self.model: Final[str] = model
        self.prompt = prompt

    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:
        if not self.valid:
            return []

        logger.log_multiline("[LiteLLM REQUEST]:", request, "debug")

        system_message = {"content": self.prompt["system"], "role": "system"}
        user_message = {"content": request, "role": "user"}

        result = completion(model=self.model, messages=[system_message, user_message])

        answers = []

        if len(result["choices"]) > 0:
            for variant in result["choices"]:
                answers.append(variant["message"]["content"])

        logger.log_multiline("[LiteLLM ANSWERS]:", answers[0], "debug")

        return answers

    def validate_env(self, key: str, message: str) -> None | str:
        if os.getenv(key) is None:
            logger.warning(message.format(key=key))
            self.valid = False
        else:
            return os.getenv(key)
