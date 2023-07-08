# Copyright: Hallux team, 2023

from __future__ import annotations
from abc import abstractmethod
from targets.diff_target import DiffTarget
from backend.query_backend import QueryBackend
from contextlib import contextmanager
from pathlib import Path
import os
from utils.logger import logger

@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    logger.debug(f"code_pocessor.set_directory: {path}")

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


class CodeProcessor:
    def __init__(self, query_backend: QueryBackend, diff_target: DiffTarget, config: dict, verbose: bool = False):
        self.query_backend: QueryBackend = query_backend
        self.diff_target: DiffTarget = diff_target
        self.config = config
        self.verbose: bool = verbose

    @abstractmethod
    def process(self):
        pass
