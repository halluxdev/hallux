#!/bin/bash

cd "${0%/*}/.."

HALLUX_VERSION=$(cat version.txt)

HALLUX_ROOT="${HALLUX_ROOT:-$(pwd)}"

rm -rf ./venv
python3 -m venv --prompt="Hallux-${HALLUX_VERSION}" "${HALLUX_ROOT}/venv"

source ./venv/bin/activate
pip install pip --upgrade
pip install wheel
pip install -r requirements.txt
