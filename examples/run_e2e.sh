#!/usr/bin/env bash
# Layer 3 example: run the behavioral E2E test against a running app instance.
#
# Requirements: Node 20+, @playwright/test installed (npm install), and
# BASE_URL pointing at a running instance of the app under test.
set -euo pipefail

if [[ -z "${BASE_URL:-}" ]]; then
  echo "BASE_URL is not set. Point it at a running app instance, e.g.:" >&2
  echo "  export BASE_URL=http://localhost:3000" >&2
  exit 1
fi

cd "$(dirname "$0")/.."
npx playwright test e2e/
