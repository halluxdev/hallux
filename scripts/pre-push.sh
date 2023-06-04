#!/usr/bin/env bash

set -e

#echo "RUN CLANG-FORMAT"
#./scripts/pre-push-format.sh

cd "${0%/*}/../.."

./ci-python-tests.sh
if [ $? -ne 0 ]; then
 echo "!!!!!PYTHON TESTS MUST PASS BEFORE GIT PUSH!!!!!"
 exit 1
fi

#../ci-cpp-tests.sh
#if [ $? -ne 0 ]; then
# echo "!!!!!C++ TESTS MUST PASS BEFORE GIT PUSH!!!!!"
# exit 1
#fi

#echo "CHECK UNIT-TESTS"
#./scripts/run-tests.sh
#
## $? stores exit value of the last command
#if [ $? -ne 0 ]; then
# echo "!!!!!TESTS MUST PASS BEFORE GIT PUSH!!!!!"
# exit 1
#fi
