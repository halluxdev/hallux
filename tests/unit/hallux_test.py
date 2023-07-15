#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import patch

from hallux import Hallux, main

import yaml
from tempfile import TemporaryDirectory



def test_hallux():
    assert "python" in Hallux.default_plugins
    assert "cpp" in Hallux.default_plugins
    assert "sonar" in Hallux.default_plugins


@pytest.mark.parametrize(
    "argv, config, expected",
    [
        ([], {}, {}),
        ([], {"whatever": {}}, {"whatever": {}}),
        (["--python"], {}, {"python": {"ruff": "."}}),
        (["--cpp"], {}, {"cpp": {"compile": True}}),
        (["--sonar"], {}, {"sonar": True}),
    ],
)
def test_init_plugins(argv: list[str], config: dict, expected: dict):
    argv = ["hallux", "fix"] + argv
    actual = Hallux.init_plugins(argv, config)
    assert actual == expected


@patch("builtins.print")
def test_Hallux_main(mock_print):
    random_path = Path("/tmp/ertyuikjhg")
    # prints usage, and quits
    out_val: int = main([], random_path)
    assert out_val == 0
    assert len(mock_print.mock_calls) == 34

    # same as before
    mock_print.mock_calls.clear()
    out_val: int = main(["hallux"], random_path)
    assert out_val == 0
    assert len(mock_print.mock_calls) == 34

    # ask for fix, but nothing configured => quit
    mock_print.mock_calls.clear()
    out_val = main(["hallux", "fix"], random_path)
    assert out_val == 0
    assert len(mock_print.mock_calls) == 0

    # asked to fix python, but nothing configured => returns 3
    mock_print.mock_calls.clear()
    out_val = main(["hallux", "fix", "--python"], random_path)
    assert out_val == 3



# This is just a placeholder for the actual name of your CONFIG_FILE
CONFIG_FILE = 'config.yml'

def test_find_config():
    with TemporaryDirectory() as tmpdir:
        # Create a config file
        config_path = Path(tmpdir)
        config_file = config_path / CONFIG_FILE
        config_dict = {"key": "value"}
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f)

        # Run the find_config method and check the output
        output_dict, output_path = Hallux.find_config(config_path)

        assert output_dict == config_dict
        assert output_path == config_path

        # Test when config file does not exist
        empty_dir = Path(tmpdir) / 'empty_dir'
        empty_dir.mkdir()
        output_dict, output_path = Hallux.find_config(empty_dir)

        assert output_dict == {}
        assert output_path == empty_dir
