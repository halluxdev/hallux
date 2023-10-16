#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from hallux.targets.gitlab_suggestion import GitlabSuggestion


def test_github_suggestion():
    (api_url, proj_name, MR_IID) = GitlabSuggestion.parse_mr_url("https://gitlab.com/hallux/hallux/-/merge_requests/2")
    assert api_url == "https://gitlab.com/api/v4"
    assert proj_name == "hallux%2Fhallux"
    assert MR_IID == 2
    assert GitlabSuggestion.parse_mr_url("https://github.com/hallux/hallux/-/merge_requests/2") is None
    assert GitlabSuggestion.parse_mr_url("https://gitlab.com/halluxhallux/-/merge_requests/2") is None
    assert GitlabSuggestion.parse_mr_url("https://gitlab.com/hallux/hallux-/merge_requests/2") is None
    assert GitlabSuggestion.parse_mr_url("https://gitlab.com/hallux/hallux/-merge_requests/2") is None


#
# @pytest.mark.skipif("GITLAB_TOKEN" not in os.environ.keys(), reason="GITLAB_TOKEN is not provided")
# def test_gitlab_access():
#     gitlab = GitlabSuggestion("https://gitlab.com/hallux/hallux/-/merge_requests/2")
#     assert gitlab.mr_iid == 2
#     assert gitlab.base_sha == "711e79030a933c60959daaea9850eb07f49e0a8f"
#     assert gitlab.start_sha == "711e79030a933c60959daaea9850eb07f49e0a8f"
#     assert gitlab.head_sha == "be17ffe7211e232aeaf3f142bf2e647786e551db"
#     assert "hallux/targets/github_suggestion.py" in gitlab.changed_files
#
#
# @pytest.mark.skipif("GITLAB_TOKEN" not in os.environ.keys(), reason="GITLAB_TOKEN is not provided")
# def test_gitlab_test_gitlab():
#     base_url = "https://gitlab.com/api/v4"
#     project_name = "hallux%2Fhallux"
#     mr_iid = 2
#     data = {}
#     data["position[position_type]"] = "text"
#     data["position[base_sha]"] = "711e79030a933c60959daaea9850eb07f49e0a8f"
#     data["position[head_sha]"] = "be17ffe7211e232aeaf3f142bf2e647786e551db"
#     data["position[start_sha]"] = "711e79030a933c60959daaea9850eb07f49edef"
#     diff_lines = " -14,15 +17,18 "
#     old_lines, new_lines = GitlabSuggestion.parse_diff_line_numbers(diff_lines)
#     assert old_lines == [14, 15]
#     assert new_lines == [17, 18]
#
#     data["position[old_path]"] = "hallux/targets/github_proposal.py"
#     data["position[new_path]"] = "hallux/targets/github_suggestion.py"
#     data["position[new_line]"] = "18"
#     data["position[old_line]"] = "18"
#     data["body"] = "Suka Blya!\n```suggestion:-0+0\nclass GithubSuggestion(FilesystemTarget):\n```"
#     request_url: str = f"{base_url}/projects/{project_name}/merge_requests/{mr_iid}/discussions"
#     headers = {"PRIVATE-TOKEN": f"{os.environ['GITLAB_TOKEN']}"}  # , "Content-Type": "text"
#     mr_response = requests.post(request_url, headers=headers, data=data)
#     print(mr_response.status_code)
#     print(mr_response.text)
#     assert mr_response.status_code == 201
#     mr_json = mr_response.json()
#     assert mr_json is not None
#     assert len(mr_json["id"]) > 10
#     assert "individual_note" in mr_json


def test_find_old_code_line():
    test_str = (
        "--- a/.github/workflows/pull_request.yml\n+++ b/.github/workflows/pull_request.yml\n@@ -3,6 +3,7 @@ name: Pull"
        " Request Pipeline\n on:\n   pull_request:\n     branches: [ master ]\n+    types: [opened, synchronize,"
        " reopened]\n \n env:\n   BUILD_TYPE: Release\n@@ -35,17 +36,17 @@ jobs:\n           tests/unit \\\n          "
        " tests/integration/hallux_fix_test.py\n \n-    - uses: sonarsource/sonarqube-scan-action@master\n-     "
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
    assert GitlabSuggestion.find_old_code_line(test_str, start_line=6) is None
    assert GitlabSuggestion.find_old_code_line(test_str, start_line=10) == 9
    assert GitlabSuggestion.find_old_code_line(test_str, start_line=35) == 34
    assert GitlabSuggestion.find_old_code_line(test_str, start_line=36) == 35
    assert GitlabSuggestion.find_old_code_line(test_str, start_line=39) == 43
    assert GitlabSuggestion.find_old_code_line(test_str, start_line=42) is None
    assert GitlabSuggestion.find_old_code_line(test_str, start_line=45) == 44
    assert GitlabSuggestion.find_old_code_line(test_str, start_line=48) is None
    assert GitlabSuggestion.find_old_code_line(test_str, start_line=57) is None
    assert GitlabSuggestion.find_old_code_line(test_str, start_line=58) == 57


# @pytest.mark.skipif("GITLAB_TOKEN" not in os.environ.keys(), reason="GITLAB_TOKEN is not provided")
# def test_gitlab_write_suggestion_changed_line():
#     gitlab = GitlabSuggestion("https://gitlab.com/hallux/hallux/-/merge_requests/2")
#     issue = TestingIssue(
#         filename="hallux/targets/github_suggestion.py",
#         description="This is description for CHANGED LINE!",
#         issue_line=17,
#         base_path=Path("/home/sergey/git/hallux"),
#     )
#
#     proposal = SimpleProposal(issue, radius_or_range=0)
#     proposal.proposed_lines = ["Here is Proposed Change"]
#     assert gitlab.write_suggestion(proposal)
#
#
# @pytest.mark.skipif("GITLAB_TOKEN" not in os.environ.keys(), reason="GITLAB_TOKEN is not provided")
# def test_gitlab_write_suggestion_not_changed_line():
#     gitlab = GitlabSuggestion("https://gitlab.com/hallux/hallux/-/merge_requests/2")
#     issue = TestingIssue(
#         filename="hallux/targets/github_suggestion.py",
#         description="This is description for NOT CHANGED LINE!",
#         issue_line=20,
#         base_path=Path("/home/sergey/git/hallux"),
#     )
#
#     proposal = SimpleProposal(issue, radius_or_range=0)
#     proposal.proposed_lines = ["Another Proposed Change"]
#     assert gitlab.write_suggestion(proposal)
