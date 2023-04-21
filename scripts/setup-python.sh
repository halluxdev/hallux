#!/bin/bash

cd "${0%/*}/.."

#PROJ_ROOT="."

rm -rf ./venv
#python3 -m venv --prompt="Hallux-0.1" "${PROJ_ROOT}/venv"
python3 -m venv --prompt="Hallux-0.1" "./venv"

source ./venv/bin/activate
pip install pip --upgrade
pip install wheel
pip install -r requirements.txt
