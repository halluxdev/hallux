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
        self.method = "GET"
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

    def query(self, request: str, issue: IssueDescriptor | None = None, issue_lines: list[str] = list) -> list[str]:

        # print(f"RestBackend.query: {request}, {issue}, {issue_lines}, {self.url}")
        print("\n\n\n\n =========== RestBackend.query ========= \n\n")
        # print(f"{self.request_body}")
        json_data = json.dumps(self.request_body)
        print(json_data)



        return []

        # response = requests.post(self.url, json={"message": request})

        # Check the response status code
        if response.status_code == 200:
            data = response.text
            print("\n\n\n\n =========== Response ========= \n\n")
            print(data)
            # Do something with the data
        else:
            print('An error occurred:', response.status_code)
            return []


        return []
