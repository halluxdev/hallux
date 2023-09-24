# Copyright: Hallux team, 2023

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Final

import openai
from openai.api_resources import ChatCompletion

from ..backends.query_backend import QueryBackend
from ..issues.issue import IssueDescriptor


class OpenAiChatGPT(QueryBackend):
    def __init__(
        self,
        model: str = "",
        max_tokens: int = 4097,
        type="openai",
        base_path: Path = Path(),
        previous_backend: QueryBackend | None = None,
    ):
        assert type == "openai"
        super().__init__(base_path, previous_backend)
        self.valid = True
        if model is None or len(model) < 2:
            logging.warning(f"Wrong model name for OpenAI Backend: {model}")
            self.valid = False

        if os.getenv("OPENAI_API_KEY") is None:
            logging.warning(
                "Environment variable OPENAI_API_KEY is required for OpenAI Backend")
            self.valid = False

        self.model: Final[str] = model
        self.max_tokens: Final[int] = max_tokens

        openai.api_key = os.getenv("OPENAI_API_KEY")

    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:
        if not self.valid:
            return []

        logging.debug("[OpenAI REQUEST]:")
        logging.debug(request)
        result = ChatCompletion.create(
            messages=[{"role": "user", "content": request}], model=self.model)
        answers = []
        if len(result["choices"]) > 0:
            for variant in result["choices"]:
                answers.append(variant["message"]["content"])

        logging.debug("[OpenAI ANSWERS]:")
        for ans in answers:
            for line in ans.split("\n"):
                logging.debug(line)

        return answers
