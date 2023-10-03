#!/usr/bin/env bash

source ./activate.sh

./hallux-test.sh -x

VERSION="$(git describe --long)"

sonar-scanner -Dsonar.host.url=https://sonarqube.hallux.dev -Dsonar.token=${SONARQUBE_TOKEN} -Dsonar.projectVersion="${VERSION}"