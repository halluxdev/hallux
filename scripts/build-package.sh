#!/usr/bin/env bash

cd "${0%/*}/.."

rm -rf dist/*

./scripts/set-version.sh

python3 -m build
