#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from hallux.proposals.simple_proposal import SimpleProposal
from hallux.targets.gitlab_suggestion import GitlabSuggestion
from tests.unit.common.testing_issue import TestingIssue

test_unidiff_str = (
    "--- a/.github/workflows/pull_request.yml\n+++ b/.github/workflows/pull_request.yml\n@@ -3,6 +3,7 @@ name: Pull"
    " Request Pipeline\n on:\n   pull_request:\n     branches: [ master ]\n+    types: [opened, synchronize,"
    " reopened]\n \n env:\n   BUILD_TYPE: Release\n@@ -35,17 +36,17 @@ jobs:\n           tests/unit \\\n          "
    " tests/integration/hallux_fix_test.py\n \n-    - uses: sonarsource/sonarqube-scan-action@v2.3.0\n-     "
    " env:\n-        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}\n-        SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL"
    " }}\n-        SONAR_PROJECT_VERSION: ${{ github.run_number }}\n \n+    - name: SonarCloud Scan\n+      uses:"
    " SonarSource/sonarcloud-github-action@master\n+      env:\n+        GITHUB_TOKEN: ${{"
    " secrets.HALLUX_GITHUB_TOKEN }}  # Needed to get PR information, if any\n+        SONAR_TOKEN: ${{"
    " secrets.SONAR_CLOUD_TOKEN }}\n \n     - name: Try to fix Sonar issues\n       env:\n-        SONAR_TOKEN: ${{"
    " secrets.SONAR_TOKEN }}\n-        SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}\n+        SONAR_TOKEN: ${{"
    " secrets.SONAR_CLOUD_TOKEN }}\n+        SONAR_HOST_URL: https://sonarcloud.io\n         SONAR_PROJECT_VERSION:"
    " ${{ github.run_number }}\n         GITHUB_TOKEN: ${{ secrets.HALLUX_GITHUB_TOKEN }}\n         OPENAI_API_KEY:"
    " ${{ secrets.OPENAI_API_KEY }}\n@@ -53,5 +54,5 @@ jobs:\n \n         export PYTHONPATH=$(pwd):${PYTHONPATH}\n "
    '        echo "python3 ./hallux/main.py --sonar --gpt3 --github https://github.com/halluxdev/hallux/pull/${{'
    ' github.event.pull_request.number }} hallux"\n-        LOG_LEVEL=DEBUG python3 ./hallux/main.py --sonar --gpt3'
    " --github https://github.com/halluxdev/hallux/pull/${{ github.event.pull_request.number }} hallux\n+       "
    " LOG_LEVEL=DEBUG python3 ./hallux/main.py --sonar=pullRequest=${{ github.event.pull_request.number }} --gpt3"
    " --github https://github.com/halluxdev/hallux/pull/${{ github.event.pull_request.number }} hallux\n \n"
)


def setup_token(self):
    # Mock the "GITLAB_TOKEN" environment variable
    self.env_patch = patch.dict(os.environ, {"GITLAB_TOKEN": "your_token"})
    self.env_patch.start()


# test missing GITLAB_TOKEN
class TestGitlabSuggestionNoToken(unittest.TestCase):
    def test_no_token(self):
        # Clean environment variables
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemError):
                GitlabSuggestion(mr_url="https://gitlab.com/hallux/hallux/-/merge_requests/2")


# test invalid MR URL
class TestGitlabSuggestionInvalidUrl(unittest.TestCase):
    def test_invalid_url(self):
        setup_token(self)
        with self.assertRaises(SystemError):
            GitlabSuggestion(mr_url="https://invalid.url.format/merge_requests/2")


# test invalid response code
class TestGitlabSuggestionInvalidResponse(unittest.TestCase):
    def test_invalid_response(self):
        setup_token(self)

        # Patch requests.get to control its behavior
        self.requests_get_patch = patch("requests.get")
        self.mock_requests_get = self.requests_get_patch.start()
        self.mock_requests_get.return_value.status_code = 400
        self.mock_requests_get.return_value.text = "Some error message"
        with self.assertRaises(SystemError):
            GitlabSuggestion(mr_url="https://gitlab.com/hallux/hallux/-/merge_requests/2")


class TestGitlabSuggestion(unittest.TestCase):
    def setUp(self):
        setup_token(self)

        # Patch requests.get to control its behavior
        self.requests_get_patch = patch("requests.get")
        self.mock_requests_get = self.requests_get_patch.start()
        self.mock_requests_get.return_value.status_code = 200
        self.mock_requests_get.return_value.json.return_value = {
            "diff_refs": {"base_sha": "base_sha", "head_sha": "some_head_sha", "start_sha": "start_sha"},
            "changes": [],
            "merged_at": None,
            "closed_at": None,
        }

        self.check_output_patch = patch("subprocess.check_output")
        self.mock_check_output = self.check_output_patch.start()
        self.mock_check_output.return_value = b"some_head_sha"
        self.gitlab_suggestion = GitlabSuggestion(mr_url="https://gitlab.com/hallux/hallux/-/merge_requests/2")
        self.addCleanup(self.env_patch.stop)
        self.addCleanup(self.requests_get_patch.stop)
        self.addCleanup(self.check_output_patch.stop)

    def test_parse_mr_url(self):
        # Shall support gitlab.com URLs
        url = "https://gitlab.com/hallux/hallux/-/merge_requests/2"
        assert GitlabSuggestion.parse_mr_url(url) == ("https://gitlab.com/api/v4", "hallux%2Fhallux", 2)

        # Shall support custom domains
        url = "https://BUSINESS.com/hallux/hallux/-/merge_requests/2"
        assert GitlabSuggestion.parse_mr_url(url) == ("https://BUSINESS.com/api/v4", "hallux%2Fhallux", 2)

        # Shall support API URLs
        url = "https://BUSINESS.com/api/v4/POJECT_NAME/-/merge_requests/17"
        assert GitlabSuggestion.parse_mr_url(url) == ("https://BUSINESS.com/api/v4", "POJECT_NAME", 17)

        # Shall support custom domains and custom routes
        url = "https://SUBDOMAIN.BUSINESS.com/ROUTE/api/v4/PROJECT_ID/-/merge_requests/17"
        assert GitlabSuggestion.parse_mr_url(url) == ("https://SUBDOMAIN.BUSINESS.com/ROUTE/api/v4", "PROJECT_ID", 17)

        assert GitlabSuggestion.parse_mr_url("github.com/hallux/hallux/-/merge_requests/2") is None
        assert GitlabSuggestion.parse_mr_url("https://gitlab.com/halluxhallux/-/merge_requests/2") is None
        assert GitlabSuggestion.parse_mr_url("https://gitlab.com/hallux/hallux-/merge_requests/2") is None
        assert GitlabSuggestion.parse_mr_url("https://gitlab.com/hallux/hallux/-merge_requests/2") is None

    def test_write_suggestion(self):
        # Test the write_suggestion method
        issue = TestingIssue(
            filename=__file__,
            description="This is some description!",
            issue_line=1,
            base_path=Path(__file__),
        )

        proposal = SimpleProposal(issue, radius_or_range=0)
        proposal.proposed_lines = ["Here is Proposed Change"]

        requests_post_patch = patch("requests.post")
        mock_requests_post = requests_post_patch.start()
        mock_requests_post.return_value.status_code = 200
        mock_requests_post.return_value.json.return_value = {
            "diff_refs": {"base_sha": "base_sha", "head_sha": "some_head_sha", "start_sha": "start_sha"},
            "changes": [],
            "merged_at": None,
            "closed_at": None,
        }

        self.gitlab_suggestion.changed_files[__file__] = __file__
        self.gitlab_suggestion.changed_diffs[__file__] = test_unidiff_str
        assert self.gitlab_suggestion.write_suggestion(proposal)
        mock_requests_post.assert_called_once()

    def test_find_old_code_line(self):
        assert GitlabSuggestion.find_old_code_line(test_unidiff_str, start_line=6) is None
        assert GitlabSuggestion.find_old_code_line(test_unidiff_str, start_line=10) == 9
        assert GitlabSuggestion.find_old_code_line(test_unidiff_str, start_line=35) == 34
        assert GitlabSuggestion.find_old_code_line(test_unidiff_str, start_line=36) == 35
        assert GitlabSuggestion.find_old_code_line(test_unidiff_str, start_line=39) == 43
        assert GitlabSuggestion.find_old_code_line(test_unidiff_str, start_line=42) is None
        assert GitlabSuggestion.find_old_code_line(test_unidiff_str, start_line=45) == 44
        assert GitlabSuggestion.find_old_code_line(test_unidiff_str, start_line=48) is None
        assert GitlabSuggestion.find_old_code_line(test_unidiff_str, start_line=57) is None
        assert GitlabSuggestion.find_old_code_line(test_unidiff_str, start_line=58) == 57

    # Test the apply_diff method
    def test_apply_diff(self):
        diff = SimpleProposal(
            TestingIssue(
                filename=__file__,
                description="This is some description!",
                issue_line=1,
                base_path=Path(__file__),
            ),
            radius_or_range=0,
        )
        diff.proposed_lines = ["Here is Proposed Change"]

        # Shall return False if the file is not in the list
        assert self.gitlab_suggestion.apply_diff(diff) is False

        # Patch FilesystemTarget.apply_diff
        apply_diff_patch = patch("hallux.targets.filesystem.FilesystemTarget.apply_diff")
        apply_diff_patch.start()

        # Shall return True if the file is in the list
        self.gitlab_suggestion.changed_files[__file__] = __file__
        assert self.gitlab_suggestion.apply_diff(diff) is True

    # Test the revert_diff method
    def test_revert_diff(self):
        # Patch FilesystemTarget.revert_diff
        revert_diff_patch = patch("hallux.targets.filesystem.FilesystemTarget.revert_diff")
        mock_revert_diff = revert_diff_patch.start()

        self.gitlab_suggestion.revert_diff()
        mock_revert_diff.assert_called_once()


if __name__ == "__main__":
    unittest.main()
