# Copyright: Hallux team, 2023

from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from backends.query_backend import QueryBackend
from issues.issue import IssueDescriptor
import requests

class RestBackend(QueryBackend):
    def __init__(
        self,
        url: str,
        request_body: Any = "$PROMPT",
        response_body: str = "",
        token: str | None = None,
        type="rest",
        base_path: Path = Path(),
        previous_backend: QueryBackend | None = None,
        verbose: bool = False,
    ):
        super().__init__(base_path, previous_backend, verbose=verbose)
        assert type == "rest"
        self.url = url
        self.token = token
        self.method = "POST"
        self.headers = {}
        self.request_body = request_body
        self.response_body = response_body

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

    def _make_request(self, request: str):
        try:
            response = requests.post(self.url, json={"message": request})

            # Successful response
            if response.status_code == 200:
                return response.json()

            else:
                print(f"Error status code: {response.status_code}")

        except requests.ConnectionError:
            print(f"Host {self.url} is not reachable.")

        return None


    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:
        if(self._is_object(self.request_body)):
            json_data = json.dumps(self.request_body)
            parsed_request = json_data.replace("$PROMPT", request)
            self.headers.update({'Content-Type': 'application/json'})

        elif(self._is_string(self.request_body)):
            parsed_request = self.request_body.replace("$PROMPT", request)
            self.headers.update({'Content-Type': 'text/plain'})

        else:
            print("Invalid request body")
            return []

        if self.verbose:
            print("REQUEST")
            print(parsed_request)

        response = self._make_request(parsed_request)
        if(response is None):
            return []

        if self.verbose:
            print("ANSWERS")
            print(response)

        answers = [response]
        return answers

