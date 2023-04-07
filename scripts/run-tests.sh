#!/usr/bin/env bash

# if any command inside script returns error, exit and return that error 
set -e

cd "${0%/*}/.."
CURR_DIR=$(pwd)

mkdir -p /tmp/hallux_test
cd /tmp/hallux_test
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SAMPLES=OFF $CURR_DIR
make -j4
ctest


