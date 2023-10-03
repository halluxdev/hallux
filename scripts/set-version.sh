#!/usr/bin/env bash

cd "${0%/*}/.."

# Relies on the git tag
MAJOR=$(git describe --long | awk -F "-" '{print $1}')
DISTANCE=$(git describe --long | awk -F "-" '{print $2}')
VERSION=${MAJOR}.${DISTANCE}

echo -n ${VERSION} > hallux/VERSION;
