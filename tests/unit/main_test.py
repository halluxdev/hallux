#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

import os
import requests
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, mock_open, patch

import github
import pytest
import yaml

from hallux.auxilary import set_directory
from hallux.backends.factory import QueryBackend
from hallux.main import CONFIG_FILE, Hallux, main
from hallux.targets.filesystem import FilesystemTarget
from hallux.tools.factory import IssueSolver


@patch("builtins.print")
def test_hallux_main(mock_print):
    # prints usage, and quits
    out_val: int = main([])
    assert out_val == 0
    assert len(mock_print.mock_calls) > 10

    # same as before
    mock_print.mock_calls.clear()
    out_val: int = main(["hallux"])
    assert out_val == 0
    assert len(mock_print.mock_calls) > 10

    # ask for fix . in empty dir
    mock_print.mock_calls.clear()
    with TemporaryDirectory() as t:
        with set_directory(t):
            out_val = main(["hallux", "--cache", "."])
            assert out_val == 0
            assert len(mock_print.mock_calls) >= 2

    mock_print.mock_calls.clear()
    with TemporaryDirectory() as t:
        with set_directory(t):
            out_val = main(["hallux", "--cache", "--verbose", "."])
            assert out_val == 0
            assert len(mock_print.mock_calls) >= 2

    # asked to fix python, but no path
    mock_print.mock_calls.clear()
    out_val = main(["hallux", "--cache", "--python"])
    assert 10 > out_val > 0


def test_find_config():
    with TemporaryDirectory() as tmpdir:
        # Create a config file
        config_path = Path(tmpdir)
        config_file = config_path / CONFIG_FILE
        config_dict = {"key": "value"}
        with open(config_file, "w") as f:
            yaml.dump(config_dict, f)

        # Run the find_config method and check the output
        output_dict, output_path = Hallux.find_config(config_path)

        assert output_dict == config_dict
        assert output_path == config_path

        # When run from inner directory => config is still can be found
        empty_dir = Path(tmpdir) / "empty_dir"
        empty_dir.mkdir()
        output_dict, output_path = Hallux.find_config(empty_dir)

        assert output_dict == config_dict
        assert output_path == config_path

        # When config_file is gone => config is not found
        config_file.unlink()
        output_dict, output_path = Hallux.find_config(empty_dir)

        assert output_dict == {}
        assert output_path == empty_dir


@pytest.mark.skipif("GITLAB_TOKEN" not in os.environ.keys(), reason="GITLAB_TOKEN is not provided")
@pytest.mark.skipif("GITHUB_TOKEN" not in os.environ.keys(), reason="GITHUB_TOKEN is not provided")
def test_init_target():

    try:
        requests.head("https://api.github.com")
    except requests.ConnectionError:
        pytest.skip(reason="No internet connectivity")

    with pytest.raises(SystemError):
        argv = ["hallux", "--cache", "--python", "--github=https://wrong.addr.com/no", "."]
        Hallux.init_target(argv, {})

    with pytest.raises(github.GithubException):
        argv = [
            "hallux",
            "--cache",
            "--python",
            "--github=https://github.com/sdasdfsadasdas/dgdgdfgdfg/pull/5655545",
            ".",
        ]
        Hallux.init_target(argv, {})

    with pytest.raises(SystemError):
        argv = ["hallux", "--cache", "--python", "--gitlab=https://wrong.addr.com/no", "."]
        Hallux.init_target(argv, {})

    with pytest.raises(SystemError):
        argv = [
            "hallux",
            "--cache",
            "--python",
            "--gitlab=https://github.com/sdasdfsadasdas/dgdgdfgdfg/pull/5655545",
            ".",
        ]
        Hallux.init_target(argv, {})


# Test for the get_version function
@patch("builtins.open", new_callable=mock_open, read_data="1.0.0")
def test_get_version(mock_file):
    from hallux.main import get_version

    assert get_version() == "1.0.0"


# Test for the main function with help argument
@patch("hallux.main.Hallux.print_usage")
def test_main_help(mock_print_usage):
    argv = ["hallux", "--help"]
    assert main(argv) == 0
    mock_print_usage.assert_called_once()


# Test for the main function with invalid directory
@patch("hallux.main.logger")
def test_main_invalid_directory(mock_logger):
    argv = ["hallux", "invalid_dir"]
    assert main(argv) == 1
    mock_logger.error.assert_called_once_with("invalid_dir is not a valid DIR")
