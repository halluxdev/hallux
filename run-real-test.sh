#!/usr/bin/env bash

source ./activate.sh

LOG_LEVEL=DEBUG python -m pytest -v -s --real-openai-test  tests/integration/hallux_sonar_test.py
