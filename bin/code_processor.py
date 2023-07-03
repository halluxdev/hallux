# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import abstractmethod
from targets.diff_target import DiffTarget
from query_backend import QueryBackend
from contextlib import contextmanager
from pathlib import Path
import os


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


class CodeProcessor:
    def __init__(self, query_backend: QueryBackend, diff_target: DiffTarget, config: dict, debug: bool = False):
        self.query_backend: QueryBackend = query_backend
        self.diff_target: DiffTarget = diff_target
        self.config = config
        self.debug: bool = debug

    @abstractmethod
    def process(self):
        pass
