#!/bin/bash
source venv/bin/activate

HALLUX_ROOT="${HALLUX_ROOT:-$(pwd)}"

export HALLUX_ROOT

export PYTHONPATH="${HALLUX_ROOT}/bin:${PYTHONPATH}"

export PATH="${HALLUX_ROOT}/bin:${PATH}"