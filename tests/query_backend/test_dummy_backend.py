import pytest
import json
from pathlib import Path
from query_backend import DummyBackend, IssueDescriptor

class TestDummyBackend:
    @pytest.fixture
    def setup_dummy_backend(self):
        filename = "test.json"
        base_path = Path(".")
        with open(filename, "wt") as file:
            json.dump({"en": {"tool1": {"file1": ["issue1", "issue2"]}}}, file)
        return DummyBackend(filename, base_path)

    def test_init(self, setup_dummy_backend):
        assert setup_dummy_backend.filename == "test.json"
        assert setup_dummy_backend.base_path == Path(".")
        assert setup_dummy_backend.json == {"en": {"tool1": {"file1": ["issue1", "issue2"]}}}

    def test_query(self, setup_dummy_backend):
        issue = IssueDescriptor(language="en", tool="tool1", filename="file1", description="issue1")
        result = setup_dummy_backend.query("request", issue)
        assert result == ["issue1"]

    def test_query_no_issue(self, setup_dummy_backend):
        result = setup_dummy_backend.query("request")
        assert result == []

    def test_query_no_match(self, setup_dummy_backend):
        issue = IssueDescriptor(language="en", tool="tool1", filename="file1", description="issue3")
        result = setup_dummy_backend.query("request", issue)
        assert result == []
