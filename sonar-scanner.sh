#!/usr/bin/env bash

source ./activate.sh

./hallux-test.sh

sonar-scanner -Dsonar.projectKey=hallux  -Dsonar.sources=bin  -Dsonar.host.url=https://sonarqube.hallux.dev  -Dsonar.token=${SONAR_TOKEN} -Dsonar.projectVersion="0.1-$(git branch --show-current)-$(git rev-list --count HEAD)-$(git rev-parse --short HEAD)"