#!/usr/bin/env bash

source ./activate.sh

python -m pytest -v $1 $2\
    --cov-branch \
    --cov-report=term \
    --cov=hallux \
    --cov-report=xml \
    --cov-report=html \
    --junitxml xunit-reports/xunit-result-unit.xml \
    tests/unit \
    tests/integration || exit 1

./scripts/sonar-scanner.sh

python hallux/main.py --gpt3 --sonar --git hallux || exit 1
