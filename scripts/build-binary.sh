#!/usr/bin/env bash

cd "${0%/*}/.."

source ./activate.sh

MAJOR=$(cat ./version.txt)
VERSION=${MAJOR}.$(git rev-list --count HEAD)

echo "# Copyright: Hallux team, 2023" > bin/__version__.py
echo "" >> bin/__version__.py
echo "version=\"${VERSION}\"" >> bin/__version__.py

mkdir -p build
cd build && pyinstaller -F ../bin/hallux.py

