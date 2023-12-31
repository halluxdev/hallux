#!/usr/bin/env bash

# source ./activate.sh

VERSION="$(git describe --long)"

sonar-scanner -Dsonar.host.url=https://sonarqube.hallux.dev -Dsonar.token=${SONAR_TOKEN} -Dsonar.projectVersion="${VERSION}"