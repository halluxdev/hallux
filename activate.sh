#!/bin/bash

# get current script directory cross-platform (macOS/Linux)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
source ${SCRIPT_DIR}/venv/bin/activate

export HALLUX_ROOT="${HALLUX_ROOT:-$(SCRIPT_DIR)}"

export PYTHONPATH="${HALLUX_ROOT}/bin:${HALLUX_ROOT}/tests:${PYTHONPATH}"

export PATH="${HALLUX_ROOT}/bin:${PATH}"