# Copyright: Hallux team, 2023

from __future__ import annotations

import json
import logging
from pathlib import Path

import requests

from hallux.logger import logger

from ..backends.query_backend import QueryBackend
from ..issues.issue import IssueDescriptor


class RestBackend(QueryBackend):
    PROMPT_STRING = "$PROMPT"

    def __init__(
        self,
        url: str,
        request_body: str | dict = PROMPT_STRING,
        response_body: str = "$RESPONSE",
        token: str | None = None,
        type="rest",
        base_path: Path = Path(),
        previous_backend: QueryBackend | None = None,
        headers: dict | None = None,
        verify: bool = False,
        prompt: object = None,
    ):
        super().__init__(base_path, previous_backend)
        assert type == "rest"
        self.url = url
        self.token = token
        self.method = "POST"
        self.headers = headers or {}
        self.request_body = request_body
        self.response_body = response_body
        self.verify = verify
        self.prompt = prompt

    def _is_string(self, obj):
        if isinstance(obj, str):
            # If obj is a string, it's a valid object
            return True
        return False

    def _is_object(self, obj):
        if isinstance(obj, (list, dict, tuple)):  # Add other valid object types as needed
            # If obj is a list, dict, or tuple, it's a valid object
            return True
        return False

    def _make_request(self, request: str | dict):
        try:
            response = requests.post(url=self.url, json=request, headers=self.headers, verify=self.verify)

            # Successful response
            if response.status_code == 200:
                if response.headers["Content-Type"] == "application/json":
                    return response.json()
                else:
                    return response.text

            else:
                logger.warning(f"Error status code: {response.status_code}")

        except requests.ConnectionError:
            logger.warning(f"Host {self.url} is not reachable.")

        return None

    def _get_by_path(self, response: str | None | dict):
        keys = self.response_body.split(".")[1:]

        current = response

        try:
            for key in keys:
                if isinstance(current, dict):
                    current = current[key]
                elif isinstance(current, list):
                    if key.isdigit():
                        key = int(key)
                        current = current[key]
                    else:
                        return []
                else:
                    return []
        except (KeyError, IndexError, ValueError):
            return []

        return [current]

    """
    Takes the response object and response_body configuration in the following format:
    "$RESPONSE.answer.0.value" and returns the value of the response object at that path.
    """

    def _parse_response(self, response: str | None | dict) -> list[str]:
        if response is None:
            return []

        if self.response_body == "$RESPONSE" and self._is_string(response):
            return [response]

        elif self.response_body.startswith("$RESPONSE."):
            if isinstance(response, str):
                try:
                    response = json.loads(response)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse response as JSON")
                    return []
            return self._get_by_path(response)

        else:
            return []

    def _replace_item(self, obj, value, replace_value) -> dict:
        for k, v in obj.items():
            if isinstance(v, dict):
                obj[k] = self._replace_item(v, value, replace_value)
            elif v == value:
                obj[k] = replace_value
        return obj

    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:
        if self._is_object(self.request_body):
            parsed_request = self._replace_item(self.request_body, self.PROMPT_STRING, request)
            self.headers.update({"Content-Type": "application/json"})

        elif self._is_string(self.request_body):
            parsed_request = self.request_body.replace(self.PROMPT_STRING, request)
            self.headers.update({"Content-Type": "text/plain"})

        else:
            logger.warning("Invalid request body")
            return []

        logger.log_multiline("[RestBackend REQUEST]:", request, "debug")

        response = self._make_request(parsed_request)
        parsed_response = self._parse_response(response)

        if not parsed_response:
            logger.warning("Parsed response is empty")
            return []

        logger.log_multiline("[RestBackend ANSWERS]:", parsed_response[0], "debug")

        return parsed_response
