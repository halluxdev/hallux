# Copyright: Hallux team, 2023

from __future__ import annotations
from pathlib import Path
from backends.openai_backend import OpenAiChatGPT, QueryBackend
from backends.dummy_backend import DummyBackend
from backends.hallux_backend import HalluxBackend
from auxilary import find_arg


class BackendFactory:
    @staticmethod
    def init_backend(argv: list[str], backends_list: list[dict] | None, config_path: Path) -> QueryBackend:
        default_list = [
            {"cache": {"type": "dummy", "filename": "dummy.json"}},
            {"free": {"type": "hallux", "url": "https://free-trial.hallux.dev/api/v1"}},
            {"gpt3": {"type": "openai", "model": "gpt-3.5-turbo", "max_tokens": 4096}},
            # Gonna be enabled soon {"gpt4": {"type": "openai", "model": "gpt-4", "max_tokens": 8192}},
        ]

        backends_list: list[dict] = backends_list if backends_list is not None else default_list
        backend = None
        if not isinstance(backends_list, list) or len(backends_list) == 0:
            raise SystemError(f"BACKENDS config setting must contain non-empty list. Error in: {backends_list}")

        for name_dict in backends_list:
            BackendFactory._validate_settings(name_dict)
            short_name = list(name_dict)[0]
            settings_dict = name_dict[short_name]
            backend = BackendFactory._create_backend(settings_dict, config_path, backend)
            if find_arg(argv, "--" + short_name) > 0:
                return backend  # stop early if required by CLI
        return backend

    @staticmethod
    def _validate_settings(name_dict: dict) -> None:
        if not isinstance(name_dict, dict) or len(name_dict.items()) != 1:
            raise SystemError(f"Each BACKEND must have just one name-settings pair. Error in: {name_dict}")

        short_name = list(name_dict)[0]
        settings_dict = name_dict[short_name]

        if not isinstance(settings_dict, dict) or "type" not in settings_dict.keys():
            raise SystemError(f"Each BACKEND setting must have at least 'type' setting. Error in: {settings_dict}")

    @staticmethod
    def _create_backend(settings_dict: dict, config_path: Path, previous_backend: QueryBackend) -> QueryBackend:
        type_to_class = {"dummy": DummyBackend, "openai": OpenAiChatGPT, "hallux": HalluxBackend}
        backend_type = settings_dict["type"]
        backend_class = type_to_class.get(backend_type)
        if backend_class is None:
            raise SystemError(f"Unknown BACKEND type: {backend_type}")
        return backend_class(**settings_dict, base_path=config_path, previous_backend=previous_backend)
