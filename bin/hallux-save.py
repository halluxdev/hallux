#!/bin/env python
from __future__ import annotations
import sys
import subprocess
import os
from pathlib import Path

def clean_target_name(target: str) -> str:
    target = target.lstrip(".")
    target = target.lstrip(" ")
    return  target

def process_make_output(make_out, data_path : Path):
    targets : list[str] = str(make_out.decode('utf-8')).split('\n')
    target: str
    processed = 0
    for target in targets:
        if target.endswith(".i"):
            target = clean_target_name(target)
            target = target[:-2]
            target_path = data_path.joinpath(target)
            print(f"{target} will be redirected to {str(target_path)}")
            processed += 1

    return processed

pwd_path = Path(os.getcwd())
hallux_path = Path(os.environ["HALLUX_ROOT"])

pwd_dirs= str(pwd_path.absolute()).split("/")
print(pwd_dirs)
data_path = hallux_path.joinpath("data")
if "hallux" in pwd_dirs and "build" in pwd_dirs and "repos" in pwd_dirs:

    for i, dir in enumerate(pwd_dirs):
        if dir == "build":
            build_index = i
        if dir == "repos":
            repos_index = i

    for i in range(repos_index, build_index):
        data_path = data_path.joinpath(pwd_dirs[i])

    print(f'Will save data into: {str(data_path)}')

    make_out = subprocess.check_output(['make', 'help'])



    processed = process_make_output(make_out, data_path)
    print(f'processed {processed} targets')

else:
    print(f'Cannot process current dir')



