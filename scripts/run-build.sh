#!/usr/bin/env bash


set -e

EXIT_CODE=0

PROJECT_DIR=/tmp/worker

cd $PROJECT_DIR

cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SAMPLES=OFF $PROJECT_DIR
if [ $? -ne 0 ]; then
  exit 0
fi

make -j4
if [ $? -ne 0 ]; then
  exit 0
fi

