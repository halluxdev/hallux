#!/bin/env python
# Copyright: Hallux team, 2023

import pytest
import json
from pathlib import Path
from backend.dummy_backend import DummyBackend
from issues.issue import IssueDescriptor
import tempfile


class MyIssueDescriptor(IssueDescriptor):
    def try_fixing(self):
        # implement the try_fixing method here
        pass


class TestDummyBackend:
    @pytest.fixture
    def setup_dummy_backend(self):
        filename = tempfile.mktemp(suffix=".json", prefix="/tmp/")
        self.base_path = Path(__file__).resolve().parent
        with open(filename, "wt") as file:
            json.dump(
                {
                    "python": {
                        "tool1": {"dummy_backend_test.txt": {"issue1": ["issue1 fixed"], "issue2": ["issue2 fixed"]}}
                    }
                },
                file,
            )
        return DummyBackend(filename, self.base_path)

    def test_init(self, setup_dummy_backend):
        assert setup_dummy_backend.filename.endswith(".json")
        assert setup_dummy_backend.base_path == Path(self.base_path)
        assert setup_dummy_backend.json == {
            "python": {"tool1": {"dummy_backend_test.txt": {"issue1": ["issue1 fixed"], "issue2": ["issue2 fixed"]}}}
        }

    def test_query(self, setup_dummy_backend):
        filename = str(self.base_path.joinpath("dummy_backend_test.txt"))
        issue = MyIssueDescriptor(language="python", tool="tool1", filename=filename, description="issue1")
        result = setup_dummy_backend.query("request", issue)
        assert result == ["issue1 fixed"]

    def test_query_no_issue(self, setup_dummy_backend):
        result = setup_dummy_backend.query("request")
        assert result == []

    def test_query_no_match(self, setup_dummy_backend):
        issue = MyIssueDescriptor(
            language="python", tool="tool1", filename="dummy_backend_test.txt", description="issue3"
        )
        result = setup_dummy_backend.query("request", issue)
        assert result == []

    def test_query_no_language(self, setup_dummy_backend):
        issue = MyIssueDescriptor(language="", tool="tool1", filename="dummy_backend_test.txt", description="issue1")
        result = setup_dummy_backend.query("request", issue)
        assert result == []

    def test_query_no_tool(self, setup_dummy_backend):
        issue = MyIssueDescriptor(
            language="cpp", tool="newTool", filename="dummy_backend_test.txt", description="issue1"
        )
        result = setup_dummy_backend.query("request", issue)
        assert result == []


def test_with_no_json_file():
    if not Path("/tmp/hallux").exists():
        Path("/tmp/hallux").mkdir()

    tmp_dir = tempfile.mkdtemp(prefix="/tmp/hallux/")
    root_path = Path(tmp_dir)
    dummy_json = "dummy.json"
    assert not root_path.joinpath(dummy_json).exists()
    dummy_backend = DummyBackend(dummy_json, base_path=root_path)
    issue = MyIssueDescriptor(language="cpp", tool="newTool", filename="file1.py", description="issue1")
    answ = dummy_backend.query("request", issue)
    del dummy_backend
    assert answ == []
    assert root_path.joinpath(dummy_json).exists()

    with open(str(root_path.joinpath(dummy_json)), "rt") as file:
        json_file = json.load(file)

    assert json_file == {"cpp": {"newTool": {"file1.py": {}}}}
