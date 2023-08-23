# Copyright: Hallux team, 2023

from pathlib import Path
from tempfile import TemporaryDirectory, tempdir


def hallux_tmp_dir():
    hallux_tmp_dir = Path(tempdir) / "hallux"
    if not hallux_tmp_dir.exists():
        hallux_tmp_dir.mkdir()

    return TemporaryDirectory(dir=str(hallux_tmp_dir))
