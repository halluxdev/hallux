#!/usr/bin/env bash

# get current script directory cross-platform (macOS/Linux)
PROJECT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# set HALLUX_ROOT if not already defined
export HALLUX_ROOT="${HALLUX_ROOT:-${PROJECT_DIR}}"

source ${HALLUX_ROOT}/venv/bin/activate

export PYTHONPATH="${HALLUX_ROOT}/src:${HALLUX_ROOT}/tests:${PYTHONPATH}"

export PATH="${HALLUX_ROOT}/bin:${PATH}"