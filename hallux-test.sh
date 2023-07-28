#!/usr/bin/env bash

source ./activate.sh

python -m pytest -v \
    --cov-branch \
    --cov-report=term \
    --cov=bin \
    --cov-report=xml \
    --cov-report=html \
    --junitxml xunit-reports/xunit-result-unit.xml \
    tests/integration \
    tests/unit || exit 1

# coverage xml -o "coverage-reports/coverage-unit.xml"