#!/usr/bin/env bash

#source ./activate.sh
#./scripts/set-version.sh

python -m pytest -v $1 $2\
    --cov-branch \
    --cov-report=term \
    --cov=hallux \
    --cov-report=xml \
    --cov-report=html \
    --junitxml xunit-reports/xunit-result-unit.xml \
    tests/unit || exit 1
