#!/bin/env python
# Helper-script to extract single c++ files together with their TranslationUnits from CMake/make projects
# It is useful for gathering training/test/validation data
# Usage:
# 1. create "repos" directly in the hallux folder. (repos is ignored in the .gitignore)
# 2. git clone any C++ project in separate sub-folder within repos dir
# 3. configure it properly with cmake, choose make generator
# 4. use this script to automatically go over all make targets and gather all valid source files/Translation units in "hallus/data" folder within respective subdirectories
# 5. ...
# 6. PROFIT!


from __future__ import annotations
import sys
import shutil
import subprocess
import os
from pathlib import Path

def clean_target_name(target: str) -> str:
    target = target.lstrip(".")
    target = target.lstrip(" ")
    return  target

def process_make_output(make_output, repo_path : Path, data_path : Path) -> int:
    targets : list[str] = str(make_output.decode('utf-8')).split('\n')
    target: str
    processed = 0
    for target in targets:
        if target.endswith(".i"):
            if not data_path.exists():
                Path.mkdir(data_path, parents=True)

            target = clean_target_name(target)
            target_name = target[:-2]
            repo_files : list = os.listdir(repo_path)

            for filename in repo_files:
                if str(filename).startswith(target_name):
                    source_file = repo_path.joinpath(str(filename))
                    target_file = data_path.joinpath(str(filename))
                    if target_file.exists():
                        break
                    print(f"{str(target_file)}")

                    # create symlink to original cpp file
                    os.symlink(source_file, target_file)
                    #shutil.copyfile(source_file, target_file)

                    # create *.sh file for compiling
                    compile_output = subprocess.check_output(['make', '-n', f'{target_name}.o'])
                    compile_output.decode('utf-8')
                    compile_file = data_path.joinpath(str(filename)+".sh")
                    with open(str(compile_file), "wt") as f:
                        f.write(compile_output.decode('utf-8'))
                        f.write("\n")
                        f.close()
                    os.chmod(compile_file, mode=0o764)

                    # make a translation unit (*.i file)
                    translationunit_output = subprocess.check_output(['make', '-n', f'{target_name}.i'])
                    translationunit_command = translationunit_output.decode('utf-8')
                    translationunit_command = translationunit_command.split(">")[0]
                    translationunit_file = data_path.joinpath(str(filename)+".i.sh")
                    with open(str(translationunit_file), "wt") as f:
                        f.write(translationunit_command + " > " + str(data_path.joinpath(str(filename)+".i")))
                        f.write("\n")
                        f.close()
                    os.chmod(translationunit_file, mode=0o764)

                    processed += 1

    return processed

def process_make_recursively(make_path: Path, repo_path: Path, data_path: Path) -> int:
    inner_dirs : list = os.listdir(make_path)
    processed : int = 0
    if "Makefile" in inner_dirs:
        os.chdir(make_path)
        make_output = subprocess.check_output(['make', 'help'])
        processed = process_make_output(make_output, repo_path, data_path)

    for inner_dir in inner_dirs:
        inner_path = make_path.joinpath(str(inner_dir))
        inner_repo = repo_path.joinpath(str(inner_dir))
        if inner_path.is_dir() and inner_repo.is_dir():
            print(str(inner_path))
            processed += process_make_recursively(inner_path, inner_repo, data_path.joinpath(str(inner_dir)))

    return processed



pwd_path = Path(os.getcwd())
hallux_path = Path(os.environ["HALLUX_ROOT"])

pwd_dirs= str(pwd_path.absolute()).split("/")
print(pwd_dirs)
data_path = hallux_path.joinpath("data")
repo_path = hallux_path.joinpath("repos")
if "hallux" in pwd_dirs and "build" in pwd_dirs and "repos" in pwd_dirs:

    for i, dir in enumerate(pwd_dirs):
        if dir == "build":
            build_index = i
        if dir == "repos":
            repos_index = i

    for i in range(repos_index+1, build_index):
        data_path = data_path.joinpath(pwd_dirs[i])
        repo_path = repo_path.joinpath(pwd_dirs[i])

    print(f'Will save data into: {str(data_path)}')
    print(f'Source dir is: {str(repo_path)}')

    processed = process_make_recursively(pwd_path, repo_path, data_path)
    os.chdir(pwd_path)

    print(f'processed {processed} targets')

else:
    print(f'Cannot process current dir')



