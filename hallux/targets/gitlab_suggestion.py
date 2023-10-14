# Copyright: Hallux team, 2023

from __future__ import annotations

import copy
import os
import subprocess

from ..logger import logger
from ..proposals.diff_proposal import DiffProposal
from .filesystem import FilesystemTarget


# Saves Issue Fixes as Github proposals
class GitlabSuggestion(FilesystemTarget):
    def __init__(self, mr_url: str):
        FilesystemTarget.__init__(self)

        (base_url, repo_name, PR_ID) = GitlabSuggestion.parse_mr_url(mr_url)

    @staticmethod
    def parse_mr_url(pr_url: str) -> tuple[str, str, int] | tuple[None, None, None]:
        """
        Tries to parse Pull-Request URL to obtain base_url, repo_name and PR_ID
        :param pr_url: shall look like this: https://gitlab.com/YOUR_NAME/REPO_NAME/pull/ID
        :return: (base_url, base_url = "https://api." + url_items[0], PR_ID) OR None
        """
        # if pr_url.startswith("https://"):
        #     pr_url = pr_url[len("https://") :]
        #     url_items = pr_url.split("/")
        #     if len(url_items) == 5 and url_items[3] == "pull":
        #         if url_items[0] == "github.com":
        #             base_url = "https://api." + url_items[0]
        #         else:
        #             base_url = "https://api." + url_items[0] + "/api/v3"
        #         repo_name = url_items[1] + "/" + url_items[2]
        #         pr_id = int(url_items[4])
        #         return base_url, repo_name, pr_id
        return None, None, None
