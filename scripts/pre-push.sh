#!/usr/bin/env bash

set -e

cd "${0%/*}/../.."

echo "CHECK FORMATTING"
black bin --check || exit 1

echo "CHECK IMPORTS ORDER"
isort bin --check || exit 1

./hallux-test.sh -x
if [ $? -ne 0 ]; then
 echo "TESTS MUST PASS BEFORE PUSH!!"
 exit 1
fi
