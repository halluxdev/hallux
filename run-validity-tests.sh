#!/usr/bin/env bash

# -s flag is for printing the output of the tests to the console

python -m pytest -v $1 $2\
    --cov-branch \
    --cov-report=term \
    --cov=hallux \
    --cov-report=xml \
    --cov-report=html \
    --junitxml xunit-reports/xunit-result-unit.xml \
    tests/unit || exit 1
