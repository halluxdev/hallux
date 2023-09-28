import os
from unittest.mock import MagicMock, patch

import pytest
from unit.common.testing_issue import TestingIssue

from backends.rest_backend import RestBackend


class TestRestBackend:
    @pytest.fixture
    def setup_issue(self):
        return TestingIssue(language="en", tool="tool1", filename="file1", description="issue1")

    @pytest.fixture
    def setup_rest_backend(self):
        return RestBackend(url="https://example.com/api")

    @pytest.fixture
    def setup_rest_backend_json(self):
        return RestBackend(
            url="https://example.com/api", request_body={"query": "$PROMPT"}, response_body="$RESPONSE.answer.values.0"
        )

    @patch("requests.post")
    def test_text_response(self, mock_create, setup_rest_backend, setup_issue):
        mock_create.return_value = MagicMock(
            status_code=200, text="test text answer", headers={"Content-Type": "text/plain"}
        )
        result = setup_rest_backend.query("request", setup_issue)
        assert result == ["test text answer"]

    @patch("requests.post")
    def test_json_response(self, mock_create, setup_rest_backend_json, setup_issue):
        mock_create.return_value = MagicMock(
            status_code=200,
            json=lambda: {"answer": {"values": ["test json answer"]}},
            headers={"Content-Type": "application/json"},
        )
        result = setup_rest_backend_json.query("request", setup_issue)
        assert result == ["test json answer"]

    def test_error_response(self, setup_rest_backend_json, setup_issue):
        result = setup_rest_backend_json.query("request", setup_issue)
        assert result == []
