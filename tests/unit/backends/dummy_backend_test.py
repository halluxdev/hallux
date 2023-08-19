#!/bin/env python
# Copyright: Hallux team, 2023
from unittest.mock import Mock

import pytest
import json
from pathlib import Path
from backends.dummy_backend import DummyBackend
import tempfile

from proposals.diff_proposal import DiffProposal
from unit.common.testing_issue import TestingIssue


class TestDummyBackend:
    @pytest.fixture
    def setup_dummy_backend(self):
        filename = tempfile.mktemp(suffix=".json", prefix="/tmp/")
        self.base_path = Path(__file__).resolve().parent
        self.test_filename = str(self.base_path.joinpath("dummy_backend_test.txt"))
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
        issue = TestingIssue(language="python", tool="tool1", filename=self.test_filename, description="issue1")
        result = setup_dummy_backend.query("request", issue, ["something"])
        assert result == []

    def test_query_no_issue(self, setup_dummy_backend):
        result = setup_dummy_backend.query("request")
        assert result == []

    def test_query_no_match(self, setup_dummy_backend):
        issue = TestingIssue(language="python", tool="tool1", filename=self.test_filename, description="issue3")
        result = setup_dummy_backend.query("request", issue)
        assert result == []

    def test_query_no_language(self, setup_dummy_backend):
        issue = TestingIssue(language="", tool="tool1", filename=self.test_filename, description="issue1")
        result = setup_dummy_backend.query("request", issue)
        assert result == []

    def test_query_no_tool(self, setup_dummy_backend):
        issue = TestingIssue(language="cpp", tool="newTool", filename=self.test_filename, description="issue1")
        result = setup_dummy_backend.query("request", issue)
        assert result == []


def test_report_succesfull_fix():
    if not Path("/tmp/hallux").exists():
        Path("/tmp/hallux").mkdir()

    tmp_dir = tempfile.mkdtemp(prefix="/tmp/hallux/")
    root_path = Path(tmp_dir)
    dummy_json = "dummy.json"
    assert not root_path.joinpath(dummy_json).exists()
    dummy_backend = DummyBackend(dummy_json, base_path=root_path)
    base_path = Path(__file__).resolve().parent
    issue = TestingIssue(language="cpp", tool="newTool", filename="file1.py", description="issue1", base_path=base_path)
    proposal = Mock(spec=DiffProposal)
    proposal.issue_lines = ["aaa"]
    proposal.proposed_lines = ["bbb"]
    dummy_backend.report_succesfull_fix(issue, proposal)
    # answ = dummy_backend.query("request", issue)
    del dummy_backend
    # assert answ == []
    assert root_path.joinpath(dummy_json).exists()

    with open(str(root_path.joinpath(dummy_json)), "rt") as file:
        json_file = json.load(file)

    assert json_file == {"f9bb7fe87bb576c1b6f9efad6bd01485": "bbb"}
