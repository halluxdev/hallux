#!/usr/bin/env bash

cd "${0%/*}/.."

rm -rf dist/*

./scripts/set-version.sh

pip install build
python3 -m build
