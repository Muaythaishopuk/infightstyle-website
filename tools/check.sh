#!/usr/bin/env bash
# Runs every quality gate. All of them must pass before a change is committed.
set -euo pipefail
cd "$(dirname "$0")"
ruff format --check .
ruff check .
mypy fightcard tests
pytest
npx --yes jscpd@4 --config .jscpd.json
