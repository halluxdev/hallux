#!/usr/bin/env bash

set -e

cd "${0%/*}/../.."

echo "FORMATTING CHECK:"
black . --check

echo "IMPORT SORT CHECK:"
isort . --check

echo "LINTING CHECK:"
ruff check .


./hallux-test.sh -x --cov-fail-under=70
if [ $? -ne 0 ]; then
 echo "TESTS MUST PASS BEFORE PUSH!!"
 exit 1
fi
