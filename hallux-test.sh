#!/usr/bin/env bash

source ./activate.sh

python -m pytest -v $1 $2\
    --cov-branch \
    --cov-report=term \
    --cov=src \
    --cov-report=xml \
    --cov-report=html \
    --junitxml xunit-reports/xunit-result-unit.xml \
    tests/integration \
    tests/unit || exit 1
