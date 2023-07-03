#!/usr/bin/env bash

source ./activate.sh

python -m pytest -v \
    --cov-branch \
    --cov-report=term \
    --cov=bin \
    tests/integration \
    tests/unit

