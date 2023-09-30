#!/usr/bin/env bash

source ./activate.sh

python -m pytest -v --real-openai-test  tests/integration/hallux_fix_test.py

./scripts/sonar-scanner.sh

python hallux/main.py --openai --sonar --git bin
