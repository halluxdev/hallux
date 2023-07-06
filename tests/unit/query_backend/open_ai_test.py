import os
import pytest
from unittest.mock import patch
from backend.openai_backend import OpenAiChatGPT
from issue import IssueDescriptor


class MyIssueDescriptor(IssueDescriptor):
    def try_fixing(self):
        # implement the try_fixing method here
        pass


class TestOpenAiChatGPT:
    @pytest.fixture
    def setup_openai_chat_gpt(self):
        config = {"model": "gpt-3.5-turbo", "max_tokens": 60}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            return OpenAiChatGPT(config)

    @patch("openai.ChatCompletion.create")
    def test_query(self, mock_create, setup_openai_chat_gpt):
        # Mock the response from ChatCompletion.create
        mock_create.return_value = {
            "choices": [
                {"message": {"content": "answer1"}},
                {"message": {"content": "answer2"}},
            ]
        }

        issue = MyIssueDescriptor(language="en", tool="tool1", filename="file1", description="issue1")
        result = setup_openai_chat_gpt.query("request", issue)
        assert result == ["answer1", "answer2"]
