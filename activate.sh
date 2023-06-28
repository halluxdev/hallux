#!/bin/bash
source venv/bin/activate

export HALLUX_ROOT="${HALLUX_ROOT:-$(pwd)}"

export PYTHONPATH="${HALLUX_ROOT}/bin:${HALLUX_ROOT}/tests:${PYTHONPATH}"

export PATH="${HALLUX_ROOT}/bin:${PATH}"