#!/bin/env python
# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import yaml

from hallux.auxilary import set_directory
from hallux.main import CONFIG_FILE, Hallux, main


@patch("builtins.print")
def test_hallux_main(mock_print):
    # prints usage, and quits
    out_val: int = main([])
    assert out_val == 0
    assert len(mock_print.mock_calls) > 30

    # same as before
    mock_print.mock_calls.clear()
    out_val: int = main(["hallux"])
    assert out_val == 0
    assert len(mock_print.mock_calls) > 30

    # ask for fix . in empty dir
    mock_print.mock_calls.clear()
    with TemporaryDirectory() as t:
        with set_directory(t):
            out_val = main(["hallux", "--cache", "."])
            assert out_val == 0
            assert len(mock_print.mock_calls) == 3

    mock_print.mock_calls.clear()
    with TemporaryDirectory() as t:
        with set_directory(t):
            out_val = main(["hallux", "--cache", "--verbose", "."])
            assert out_val == 0
            assert len(mock_print.mock_calls) == 3

    # asked to fix python, but no path
    mock_print.mock_calls.clear()
    out_val = main(["hallux", "--cache", "--python"])
    assert 10 > out_val > 0  #


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
