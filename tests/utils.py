# Copyright: Hallux team, 2023

from pathlib import Path
from tempfile import TemporaryDirectory, gettempdir


def hallux_tmp_dir():
    hallux_tmp_base = Path(gettempdir()) / "hallux"
    hallux_tmp_base.mkdir(exist_ok=True)
    return TemporaryDirectory(dir=str(hallux_tmp_base))
