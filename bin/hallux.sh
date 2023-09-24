#!/usr/bin/env bash
# Copyright: Hallux team, 2023
# Developer version for local run

SCRIPT_DIR=$(dirname "$0")
HALLUX_ROOT="${SCRIPT_DIR}/.."

if [ ! -d "${HALLUX_ROOT}/venv" ]
then
  python3 -m venv --prompt="Hallux-0.2" "${HALLUX_ROOT}/venv"
  source ${HALLUX_ROOT}/venv/bin/activate
  pip install pip --upgrade
  pip install wheel
  pip install -r ${HALLUX_ROOT}/requirements.txt
fi

source ${HALLUX_ROOT}/activate.sh

python3 ${HALLUX_ROOT}/hallux/main.py "$@"
