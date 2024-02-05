#!/usr/bin/env bash

# ./scripts/sonar-scanner.sh || exit 1

export PYTHONPATH=$(pwd):${PYTHONPATH}

LOG_LEVEL=DEBUG python3 ./hallux/main.py --gpt3 --sonar --git hallux || exit 1
