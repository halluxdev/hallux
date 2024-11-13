#!/bin/env python
# Copyright: Hallux team, 2023-2024

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from hallux.backends.dummy_backend import DummyBackend
from hallux.backends.factory import BackendFactory
from hallux.backends.litellm import LiteLLMBackend
from hallux.backends.query_backend import QueryBackend
from hallux.backends.rest_backend import RestBackend

dummy = DummyBackend(Path.joinpath(Path(), "dummy-test.json"), Path())
ligthllm = LiteLLMBackend("gpt-3.5-turbo")
ligthllm_4o = LiteLLMBackend("gpt-4o")


@pytest.mark.parametrize(
    "argv, config, expected_result",
    [
        ([], {}, ligthllm),
        (["hallux", "--model=gpt-4o", "."], {}, ligthllm_4o),
        (["hallux", '--model="gpt-4o"', "."], {}, ligthllm_4o),
        (["hallux", "--model", "gpt-4o", "."], {}, ligthllm_4o),
    ],
)
def test_backend_factory(argv: list[str], config: dict[str, Any], expected_result):
    result: QueryBackend = BackendFactory.init_backend(argv, config, Path())
    assert type(result) == type(expected_result)
    if isinstance(result, LiteLLMBackend):
        assert result.model == expected_result.model


@pytest.mark.parametrize(
    "argv, config",
    [
        (["hallux", "--model", "gpt-4o"], {}),
        (["hallux", "--model", "."], {}),
        (["hallux", "--model=", "."], {}),
    ],
)
def test_wrong_behavior(argv: list[str], config: dict[str, Any]):
    with pytest.raises(SystemError):
        no_result = BackendFactory.init_backend(argv, config, Path())
