#!/bin/bash

cd "${0%/*}/.."

HALLUX_ROOT="${HALLUX_ROOT:-$(pwd)}"

rm -rf ./venv
python3 -m venv --prompt="Hallux-0.1" "${HALLUX_ROOT}/venv"

source ./venv/bin/activate
pip install pip --upgrade
pip install wheel
pip install -r requirements.txt
