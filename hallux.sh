
source venv/bin/activate

HALLUX_ROOT="${HALLUX_ROOT:-$(pwd)}"
export HALLUX_ROOT

export PYTHONPATH="${HALLUX_ROOT}/python:${PYTHONPATH}"
