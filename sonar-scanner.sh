#!/usr/bin/env bash

source ./activate.sh

./hallux-test.sh

sonar-scanner -Dsonar.projectKey=hallux  -Dsonar.sources=bin  -Dsonar.host.url=http://localhost:9000  -Dsonar.token=sqp_fa4f29ff253c20fa7c5cad652763bc6d5a582303