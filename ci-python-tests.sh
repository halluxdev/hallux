# Tests for main (python folder) part hallux project

source venv/bin/activate

set -euo pipefail

EXIT_CODE=0

#--cov=python --cov-report=html
python -m pytest -v tests/python "$@" || EXIT_CODE=$?