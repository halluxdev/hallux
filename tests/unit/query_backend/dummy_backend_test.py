#!/bin/env python
# Copyright: Hallux team, 2023

import pytest
import json
from pathlib import Path
from query_backend import DummyBackend
from issue import IssueDescriptor


class MyIssueDescriptor(IssueDescriptor):
    def try_fixing(self):
        # implement the try_fixing method here
        pass


class TestDummyBackend:
    @pytest.fixture
    def setup_dummy_backend(self):
        filename = "/tmp/test.json"
        base_path = Path("./tests/unit/query_backend")
        self.base_path = base_path
        with open(filename, "wt") as file:
            json.dump(
                {"python": {"tool1": {"file1.py": {"issue1": ["issue1 fixed"], "issue2": ["issue2 fixed"]}}}}, file
            )
        return DummyBackend(filename, base_path)

    def test_init(self, setup_dummy_backend):
        assert setup_dummy_backend.filename == "/tmp/test.json"
        assert setup_dummy_backend.base_path == Path(self.base_path)
        assert setup_dummy_backend.json == {
            "python": {"tool1": {"file1.py": {"issue1": ["issue1 fixed"], "issue2": ["issue2 fixed"]}}}
        }

    def test_query(self, setup_dummy_backend):
        filename = self.base_path.joinpath("file1.py")
        issue = MyIssueDescriptor(language="python", tool="tool1", filename=filename, description="issue1")
        result = setup_dummy_backend.query("request", issue)
        assert result == ["issue1 fixed"]

    def test_query_no_issue(self, setup_dummy_backend):
        result = setup_dummy_backend.query("request")
        assert result == []

    def test_query_no_match(self, setup_dummy_backend):
        issue = MyIssueDescriptor(language="python", tool="tool1", filename="file1.py", description="issue3")
        result = setup_dummy_backend.query("request", issue)
        assert result == []

    def test_query_no_language(self, setup_dummy_backend):
        issue = MyIssueDescriptor(language="", tool="tool1", filename="file1.py", description="issue1")
        result = setup_dummy_backend.query("request", issue)
        assert result == []

    def test_query_no_tool(self, setup_dummy_backend):
        issue = MyIssueDescriptor(language="cpp", tool="newTool", filename="file1.py", description="issue1")
        result = setup_dummy_backend.query("request", issue)
        assert result == []
