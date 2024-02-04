#!/usr/bin/env bash

python -m pytest -v $1 $2\
    --cov-branch \
    --cov-report=term \
    --cov=hallux \
    --cov-report=xml \
    --cov-report=html \
    --junitxml xunit-reports/xunit-result-unit.xml \
    tests/unit \
    tests/integration || exit 1
