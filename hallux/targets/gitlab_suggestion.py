# Copyright: Hallux team, 2023

from __future__ import annotations

import os
import subprocess
from typing import Final

import requests
from unidiff import PatchSet

from ..logger import logger
from ..proposals.diff_proposal import DiffProposal
from .filesystem import FilesystemTarget
from .github_suggestion import GithubSuggestion


# Saves Issue Fixes as Github proposals
class GitlabSuggestion(FilesystemTarget):
    def __init__(self, mr_url: str | None, verify: bool = False):
        FilesystemTarget.__init__(self)

        if "GITLAB_TOKEN" not in os.environ.keys():
            raise SystemError("GITLAB_TOKEN is not provided")

        answ = GitlabSuggestion.parse_mr_url(mr_url)
        if answ is None:
            logger.warning(f"Cannot parse gitlab MR URL: {mr_url}")
            raise SystemError(f"Cannot parse gitlab MR URL: {mr_url}")
        (base_url, project_name, mr_iid) = answ
        self.base_url: Final[str] = base_url
        self.project_name: Final[str] = project_name
        self.mr_iid: Final[int] = mr_iid
        self.verify = verify

        request_url: str = f"{base_url}/projects/{project_name}/merge_requests/{mr_iid}/changes?unidiff=true"
        headers = {"PRIVATE-TOKEN": f"{os.environ['GITLAB_TOKEN']}"}
        mr_response = requests.get(request_url, headers=headers, verify=self.verify)

        if mr_response.status_code != 200:
            logger.error(mr_response.text)
            raise SystemError(mr_response.text)

        self.mr_json = mr_response.json()
        self.base_sha: Final[str] = self.mr_json["diff_refs"]["base_sha"]
        self.head_sha: Final[str] = self.mr_json["diff_refs"]["head_sha"]
        self.start_sha: Final[str] = self.mr_json["diff_refs"]["start_sha"]

        # mapping from new_path to old_path (if file is changed)
        self.changed_files: Final[dict[str, str]] = {}
        # mapping for diffs of changed files
        self.changed_diffs: Final[dict[str, str]] = {}
        for change in self.mr_json["changes"]:
            new_path = change["new_path"]
            if new_path is not None:  # new_path is None when file is deleted
                self.changed_files[new_path] = change["old_path"]
                self.changed_diffs[new_path] = change["diff"]

        if self.mr_json["merged_at"] is not None or self.mr_json["closed_at"] is not None:
            raise SystemError(f"Merge Request {mr_iid} is either closed or merged already")

        local_git_sha: str
        try:
            git_log: str = subprocess.check_output(["git", "log", "--pretty=oneline"]).decode("utf8")
            local_git_sha = git_log.split("\n")[0].split(" ")[0]
        except Exception as e:
            raise SystemError(f"Local git commit is not available: {e}")

        if local_git_sha != self.head_sha:
            raise SystemError(
                f"Local git commit: `{local_git_sha}` "
                f"do not coinside with the head from pull-request: `{self.head_sha}` "
            )

    @staticmethod
    def parse_mr_url(mr_url: str) -> tuple[str, str, int] | None:
        """
        Tries to parse Pull-Request URL to obtain base_url, repo_name and PR_ID
        :param mr_url:
            shall a gitlab merge request URL: https://gitlab.com/hallux/hallux/-/merge_requests/2
            or a gitlab API URL: https://gitlab.com/api/v4/hallux%2Fhallux/merge_requests/2

        :return: (base_url, project_name, mr_iid) OR None
        """

        url_protocol = "https://"
        if not (mr_url.startswith(url_protocol)):
            return None

        # if mr_url includes /api/v4 - then it is an API URL
        api_prefix = "/api/v4"

        if mr_url.count(api_prefix) > 0:
            base_url = mr_url[: mr_url.find(api_prefix) + len(api_prefix)]
            project_name = mr_url[mr_url.find(api_prefix) + len(api_prefix) + 1 : mr_url.find("/merge_requests") - 2]
            mr_iid = int(mr_url[mr_url.rfind("/") + 1 :])
            return base_url, project_name, mr_iid

        mr_url = mr_url[len(url_protocol) :]

        url_items = mr_url.split("/")
        if len(url_items) == 6:
            if url_items[3] == "-" and url_items[4] == "merge_requests":
                base_url = url_protocol + url_items[0] + api_prefix
                project_name = url_items[1] + "%2F" + url_items[2]
                mr_iid = int(url_items[5])
                return base_url, project_name, mr_iid

        return None

    def apply_diff(self, diff: DiffProposal) -> bool:
        for file in self.changed_files:
            if diff.filename == file or file.endswith(diff.filename):
                FilesystemTarget.apply_diff(self, diff)
                return True
        return False

    def revert_diff(self):
        FilesystemTarget.revert_diff(self)

    @staticmethod
    def find_old_code_line(diff: str, start_line) -> int | None:
        patch_set = PatchSet(diff)
        for hunk in patch_set[0]:
            if start_line < hunk.target_start:
                return hunk.source_start + start_line - hunk.target_start

            if hunk.target_start <= start_line and start_line <= hunk.target_start + hunk.target_length:
                for line in hunk:
                    if line.target_line_no == start_line:
                        return line.source_line_no

        last_known_line = patch_set[0][-1][-1]
        return last_known_line.source_line_no + start_line - last_known_line.target_line_no

    def write_suggestion(self, proposal: DiffProposal) -> bool:
        data = {}
        data["position[position_type]"] = "text"
        data["position[base_sha]"] = self.base_sha
        data["position[head_sha]"] = self.head_sha
        data["position[start_sha]"] = self.start_sha
        data["position[new_path]"] = proposal.filename
        data["position[new_line]"] = proposal.start_line

        if self.changed_files[proposal.filename] is not None:
            data["position[old_path]"] = self.changed_files[proposal.filename]
            git_diff: str = self.changed_diffs[proposal.filename]
            old_line = self.find_old_code_line(git_diff, proposal.start_line)
            if old_line:
                data["position[old_line]"] = old_line

        body = proposal.description + "\n```suggestion"
        if proposal.end_line > proposal.start_line:
            body += f":-0+{proposal.end_line-proposal.start_line}"
        body += "\n"
        for i in range(len(proposal.proposed_lines)):
            line = proposal.proposed_lines[i]
            body += line
            body += "\n" if i < len(proposal.proposed_lines) - 1 else ""
        body = body + "\n```"
        data["body"] = body

        request_url: str = f"{self.base_url}/projects/{self.project_name}/merge_requests/{self.mr_iid}/discussions"
        headers = {"PRIVATE-TOKEN": f"{os.environ['GITLAB_TOKEN']}"}  # , "Content-Type": "text"
        mr_response = requests.post(request_url, headers=headers, data=data, verify=self.verify)

        logger.debug(mr_response.status_code)
        logger.debug(mr_response.text)
        if mr_response.status_code != 200 and mr_response.status_code != 201:
            logger.error(mr_response.text)
            return False
        return True

    def commit_diff(self) -> bool:
        success: bool = False
        try:
            compacted = GithubSuggestion.compact_proposal(self.existing_proposal)
            success = self.write_suggestion(compacted)
        finally:
            # clean local code
            FilesystemTarget.revert_diff(self)

        return success

    def requires_refresh(self) -> bool:
        return False
