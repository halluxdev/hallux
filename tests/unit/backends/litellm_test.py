import os
import pytest
from pathlib import Path
from hallux.backends.litellm import LiteLLMBackend

from unittest.mock import patch, MagicMock
from pathlib import Path
from hallux.issues.issue import IssueDescriptor
from unittest.mock import patch


@pytest.fixture
def valid_model():
    return "gpt-4o"


@pytest.fixture
def invalid_model():
    return "x"


@pytest.fixture
def setup_litellm_backend(valid_model):
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        return LiteLLMBackend(model=valid_model)


def test_initialization_valid_model(setup_litellm_backend, valid_model):
    assert setup_litellm_backend.valid
    assert setup_litellm_backend.model == valid_model


def test_initialization_invalid_model(invalid_model):
    with patch("hallux.logger.logger.warning") as mock_warning:
        backend = LiteLLMBackend(model=invalid_model)
        assert not backend.valid
        mock_warning.assert_called_once_with(f"Wrong model name for LiteLLM Backend: {invalid_model}")


@patch("hallux.backends.litellm.completion")
def test_query_valid_model(mock_completion, setup_litellm_backend):
    request = "Test request"
    expected_response = ["Test response"]

    mock_completion.return_value = {"choices": [{"message": {"content": "Test response"}}]}
    response = setup_litellm_backend.query(request)
    assert response == expected_response


def test_query_invalid_model(invalid_model):
    with patch("hallux.logger.logger.warning"):
        backend = LiteLLMBackend(model=invalid_model)
    request = "Test request"
    response = backend.query(request)
    assert response == []


def test_validate_env_present(monkeypatch):
    key = "TEST_ENV"
    value = "test_value"
    monkeypatch.setenv(key, value)
    backend = LiteLLMBackend(model="valid_model")
    result = backend.validate_env(key, "Warning: {key} is not set")
    assert result == value


def test_validate_env_missing(monkeypatch):
    key = "MISSING_ENV"
    message = "Warning: {key} is not set"
    monkeypatch.delenv(key, raising=False)

    with patch("hallux.logger.logger.warning") as mock_warning:
        backend = LiteLLMBackend(model="valid_model")
        result = backend.validate_env(key, message)
        assert result is None
        mock_warning.assert_called_once_with(message.format(key=key))
