# Copyright: Hallux team, 2023

from __future__ import annotations

from pathlib import Path
from typing import Any

from hallux.logger import logger
from hallux.models import PromptConfig

from ..auxilary import find_arg, find_argvalue
from ..backends.dummy_backend import DummyBackend
from ..backends.litellm import LiteLLMBackend
from ..backends.query_backend import QueryBackend
from ..backends.rest_backend import RestBackend


class BackendFactory:
    @staticmethod
    def init_backend(argv: list[str], config: dict[str, Any], config_path: Path) -> QueryBackend:

        prompt = BackendFactory._get_prompt(config)
        model_index = find_arg(argv, "--model")
        if model_index > 0:
            model_value = BackendFactory.validate_model_args(argv, model_index)
            if model_value is not None:
                config["backends"] = [{"model": {"type": "litellm", "model": model_value}}]

        backends_list: list[dict] | None = config.get("backends", None)

        default_list = [
            {"cache": {"type": "dummy", "filename": "dummy.json"}},
            {"gpt3": {"type": "litellm", "model": "gpt-3.5-turbo"}},
        ]

        backends_list: list[dict] = backends_list if backends_list is not None else default_list
        backend = None

        if not isinstance(backends_list, list) or len(backends_list) == 0:
            raise SystemError(f"BACKENDS config setting must contain non-empty list. Error in: {backends_list}")

        logger.log_multiline("[System prompt]", prompt.get("system"), "debug")

        for name_dict in backends_list:
            name, settings = BackendFactory._validate_settings(name_dict)
            backend = BackendFactory._create_backend(settings, config_path, backend, prompt)
            if find_arg(argv, "--" + name) > 0:
                return backend  # stop early if required by CLI
        return backend

    @staticmethod
    def validate_model_args(argv, model_index: int) -> str | None:
        model_value = find_argvalue(argv, "--model")
        if model_value and model_value != "":
            # Ensure the last argument is a valid path

            has_delimeter = "=" in argv[model_index]
            max_args = model_index + (1 if has_delimeter else 2)
            is_extra_arg_present = len(argv) > max_args
            is_last_arg_not_option = not argv[-1].startswith("--")

            if is_extra_arg_present and is_last_arg_not_option:
                path_value = argv[-1]
                if path_value:
                    return model_value
                else:
                    raise SystemError("Missing last path argument. Please provide a valid path")
            else:
                raise SystemError("Missing or invalid last path argument. Please provide a valid path.")
        else:
            raise SystemError(
                "The '--model' argument must be followed by a valid model name, like '--model=gpt4o'.\n"
                "More details on model options: https://hallux.dev/docs/user-guide/backends"
            )

    @staticmethod
    def _validate_settings(name_dict: dict) -> tuple[str, dict[str, str]]:
        if not isinstance(name_dict, dict) or len(name_dict.items()) != 1:
            raise SystemError(f"Each BACKEND must be just one name-settings pair. Error in: {name_dict}")

        name = str(list(name_dict)[0])
        settings = name_dict[name]

        if not isinstance(settings, dict) or ("type" not in settings.keys() and not settings["model"]):
            raise SystemError(
                f"Each BACKEND setting must have at least 'type' or a 'model' setting. Error in: {settings}"
            )
        return name, settings

    @staticmethod
    def _create_backend(
        settings: dict, config_path: Path, previous_backend: QueryBackend, prompt: PromptConfig
    ) -> QueryBackend:
        type_to_class = {
            "dummy": DummyBackend,
            "rest": RestBackend,
            "litellm": LiteLLMBackend,
        }

        backend_type = settings.get("type", "").strip()

        # Set litellm as the default type if none is specified
        if not backend_type:
            backend_type = "litellm"
            logger.info("No backend type specified. Using 'litellm' as a default backend type.")

        # Add backward compatibility for openai and openai.azure types
        # TODO: remove this in the future versions
        if backend_type.lower() in ["openai", "openai.azure"]:
            backend_type = "litellm"
            settings["type"] = "litellm"
            logger.warning("'openai' and 'openai.azure' backends are deprecated. Please use 'litellm' instead.")
        if backend_type.lower() == "openai.azure":
            settings["model"] = f"azure/{settings['model']}"
            logger.warning(f"Model name for 'openai.azure' updated to 'azure/{settings['model']}'.")

        backend_class = type_to_class.get(backend_type)
        if backend_class is None:
            raise SystemError(f"Unknown BACKEND type: {backend_type}. Supported types: {type_to_class.keys()}")
        return backend_class(**settings, base_path=config_path, previous_backend=previous_backend, prompt=prompt)

    @staticmethod
    def _get_prompt(config: dict) -> PromptConfig:
        default_system_message = """You are an experienced software engineer who makes code reviews.
You will be given a code snippet and a description of an issue.
Fix the issue and return ONLY the fixed code, without explanations.
Keep formatting and indentation as in the original code."""

        default_user_message = """Fix the following "{ISSUE_LANGUAGE}" "{ISSUE_TYPE}" issue: "{ISSUE_DESCRIPTION}" in "{ISSUE_FILEPATH}",
from corresponding code:\n```\n{ISSUE_LINES}\n```"""

        system_message = config.get("prompt.system", default_system_message)
        user_message = config.get("prompt.user", default_user_message)
        return {"system": system_message, "user": user_message}
