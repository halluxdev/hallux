#!/usr/bin/env bash

source ./activate.sh

#python -m pytest -v --real-openai-test  tests/integration/hallux_fix_test.py
LOG_LEVEL=DEBUG python -m pytest -v -s --real-openai-test  tests/integration/hallux_sonar_test.py

#./scripts/sonar-scanner.sh
#
#LOG_LEVEL=DEBUG python hallux/main.py --openai --sonar --git bin