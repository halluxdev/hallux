# Copyright: Hallux team, 2023

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """
    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


def find_arg(argv: list[str], name: str) -> int:
    """
    Finds argument index and list of following arguments
    """
    for i in range(len(argv)):
        arg = argv[i]
        if arg == name or arg.startswith(name):
            return i
    return -1
