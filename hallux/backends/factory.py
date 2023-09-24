# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path

from ..auxilary import find_arg
from ..backends.dummy_backend import DummyBackend
from ..backends.openai_backend import OpenAiChatGPT, QueryBackend
from ..backends.rest_backend import RestBackend


class BackendFactory:
    @staticmethod
    def init_backend(argv: list[str], backends_list: list[dict] | None, config_path: Path) -> QueryBackend:
        default_list = [
            {"cache": {"type": "dummy", "filename": "dummy.json"}},
            {"rest": {"type": "rest", "url": "http://localhost:8000/generate"}},
            {"gpt3": {"type": "openai", "model": "gpt-3.5-turbo", "max_tokens": 4096}},
            # Gonna be enabled soon {"gpt4": {"type": "openai", "model": "gpt-4", "max_tokens": 8192}},
        ]

        backends_list: list[dict] = backends_list if backends_list is not None else default_list
        backend = None
        if not isinstance(backends_list, list) or len(backends_list) == 0:
            raise SystemError(
                f"BACKENDS config setting must contain non-empty list. Error in: {backends_list}")

        for name_dict in backends_list:
            name, settings = BackendFactory._validate_settings(name_dict)
            backend = BackendFactory._create_backend(
                settings, config_path, backend)
            if find_arg(argv, "--" + name) > 0:
                return backend  # stop early if required by CLI
        return backend

    @staticmethod
    def _validate_settings(name_dict: dict) -> tuple[str, dict[str, str]]:
        if not isinstance(name_dict, dict) or len(name_dict.items()) != 1:
            raise SystemError(
                f"Each BACKEND must be just one name-settings pair. Error in: {name_dict}")

        name = str(list(name_dict)[0])
        settings = name_dict[name]

        if not isinstance(settings, dict) or "type" not in settings.keys():
            raise SystemError(
                f"Each BACKEND setting must have at least 'type' setting. Error in: {settings}")
        return name, settings

    @staticmethod
    def _create_backend(settings: dict, config_path: Path, previous_backend: QueryBackend) -> QueryBackend:
        type_to_class = {"dummy": DummyBackend,
                         "openai": OpenAiChatGPT, "rest": RestBackend}
        backend_type = settings["type"]
        backend_class = type_to_class.get(backend_type)
        if backend_class is None:
            raise SystemError(f"Unknown BACKEND type: {backend_type}")
        return backend_class(**settings, base_path=config_path, previous_backend=previous_backend)
