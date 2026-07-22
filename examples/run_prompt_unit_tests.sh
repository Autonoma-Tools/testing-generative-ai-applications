#!/usr/bin/env bash
# Layer 1 example: run the deterministic prompt unit tests.
#
# Requirements: Python 3.10+, pytest installed (pip install -r requirements.txt)
set -euo pipefail

cd "$(dirname "$0")/.."
pytest tests/ -v
