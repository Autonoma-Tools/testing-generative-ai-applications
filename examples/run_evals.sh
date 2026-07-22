#!/usr/bin/env bash
# Layer 2 example: run the eval-set tests against a DeepEval LLM judge.
#
# Requirements: Python 3.10+, deepeval installed, OPENAI_API_KEY exported.
set -euo pipefail

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is not set. DeepEval needs a judge model configured." >&2
  echo "Example: export OPENAI_API_KEY=sk-..." >&2
  exit 1
fi

cd "$(dirname "$0")/.."
pytest evals/ -v
