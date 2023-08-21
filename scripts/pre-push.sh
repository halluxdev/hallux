#!/usr/bin/env bash

set -e

cd "${0%/*}/../.."

black . --check
if [ $? -ne 0 ]; then
 echo "Python code needs formatting: run 'black .' command"
 exit 1
fi

isort . --check
if [ $? -ne 0 ]; then
 echo "Python code needs imports re-ordering: run 'isort .' command"
 exit 1
fi

./hallux-test.sh -x
if [ $? -ne 0 ]; then
 echo "TESTS MUST PASS BEFORE PUSH!!"
 exit 1
fi
