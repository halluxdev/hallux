# Copyright: Hallux team, 2023

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory


@contextmanager
def set_directory(path: str | Path | TemporaryDirectory):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """
    origin = Path().absolute()
    path_str = path.name if isinstance(path, TemporaryDirectory) else str(path)
    try:
        os.chdir(path_str)
        yield
    finally:
        os.chdir(origin)


def find_arg(argv: list[str], name: str) -> int:
    """
    Finds argument index
    """
    for i in range(len(argv)):
        arg = argv[i]
        if arg == name or arg.startswith(name):
            return i
    return -1


def find_argvalue(argv: list[str], name: str) -> str | None:
    """
    Finds argument index and following value
    """
    for i in range(len(argv)):
        arg = argv[i]
        if arg == name:  # --key value
            if len(argv) > i + 1 and not argv[i + 1].startswith("-"):
                return argv[i + 1]
        elif arg.startswith(name + "="):  # --key=value or --key="value"
            return arg.split("=")[-1].strip('"').strip("'")

    return None
