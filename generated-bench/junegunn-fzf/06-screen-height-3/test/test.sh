#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install -q pytest
pytest -q test/test_state.py
