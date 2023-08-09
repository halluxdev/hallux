#!/usr/bin/env bash

source ./activate.sh

./hallux-test.sh -x

MAJOR=$(cat version.txt)
VERSION="${MAJOR}.$(git rev-list --count HEAD)-$(git rev-parse --short HEAD)"

sonar-scanner -Dsonar.host.url=https://sonarqube.hallux.dev  -Dsonar.token=${SONAR_TOKEN} -Dsonar.projectVersion="${VERSION}"