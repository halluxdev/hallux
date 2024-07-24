#!/usr/bin/env bash

set -e

cd "${0%/*}/.."

rm -rf dist/*

./scripts/set-version.sh

pip install --upgrade build
python3 -m build
