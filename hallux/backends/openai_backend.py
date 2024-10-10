# Copyright: Hallux team, 2023

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

import openai
from openai import ChatCompletion

from hallux.logger import logger

from ..backends.query_backend import QueryBackend
from ..issues.issue import IssueDescriptor


class OpenAiChatGPT(QueryBackend):
    def __init__(
        self,
        model: str = "",
        max_tokens: int = 4097,
        type="openai",
        api_version="2021-05-15",
        base_path: Path = Path(),
        previous_backend: QueryBackend | None = None,
        prompt: object = None,
    ):
        assert type == "openai" or type == "openai.azure"
        super().__init__(base_path, previous_backend)

        self.valid = True
        if model is None or len(model) < 2:
            logger.warning(f"Wrong model name for OpenAI Backend: {model}")
            self.valid = False

        self.model: Final[str] = model
        self.max_tokens: Final[int] = max_tokens
        self.api_version: Final[int] = api_version
        self.prompt = prompt

        # For Azure OpenAI
        if type == "openai.azure":
            openai.api_key = self.validate_env(
                "AZURE_OPENAI_API_KEY", "Environment variable {key} is required for OpenAI Azure Backend"
            )
            openai.api_base = self.validate_env(
                "AZURE_OPENAI_ENDPOINT", "Environment variable {key} is required for OpenAI Azure Backend"
            )
            openai.api_type = "azure"
            openai.api_version = "2023-05-15"
        else:
            openai.api_key = self.validate_env(
                "OPENAI_API_KEY", "Environment variable {key} is required for OpenAI Backend"
            )

    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:
        if not self.valid:
            return []

        logger.debug("[OpenAI REQUEST]:")
        logger.debug(request)
        result = ChatCompletion.create(
            messages=[{"role": "user", "content": request}], model=self.model, engine=self.model
        )
        answers = []
        if len(result["choices"]) > 0:
            for variant in result["choices"]:
                answers.append(variant["message"]["content"])

        logger.debug("[OpenAI ANSWERS]:")
        for ans in answers:
            for line in ans.split("\n"):
                logger.debug(line)

        return answers

    def validate_env(self, key: str, message: str) -> None | str:
        if os.getenv(key) is None:
            logger.warning(message.format(key=key))
            self.valid = False
        else:
            return os.getenv(key)
