# Tests for main (python folder) part hallux project

source ./activate.sh

set -euo pipefail

EXIT_CODE=0

#--cov=python --cov-report=html
python -m pytest -v ${HALLUX_ROOT}/tests/python "$@" || EXIT_CODE=$?

exit "${EXIT_CODE}"