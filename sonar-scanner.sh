#!/usr/bin/env bash

source ./activate.sh

./hallux-test.sh -x

sonar-scanner -Dsonar.projectKey=halluxai_hallux_AYmdJxzWKwloFfC93W7m  -Dsonar.sources=bin  -Dsonar.host.url=https://sonarqube.hallux.dev  -Dsonar.token=${SONAR_TOKEN} -Dsonar.projectVersion="0.1-$(git branch --show-current)-$(git rev-list --count HEAD)-$(git rev-parse --short HEAD)"