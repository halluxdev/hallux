#!/usr/bin/env bash

set -e

cd "${0%/*}/.."

git describe --long

# Relies on the git tag
MAJOR=$(git describe --long | awk -F "-" '{print $1}')
DISTANCE=$(git describe --long | awk -F "-" '{print $2}')
VERSION=${MAJOR}.${DISTANCE}

echo "Setting version to ${VERSION}"
echo -n ${VERSION} > hallux/VERSION;
