#!/usr/bin/env bash
set -euo pipefail

# Run setup from repository root regardless of caller cwd.
cd "$(dirname "$0")/.."

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
pre-commit install --install-hooks

printf '\033[0;32mSetup successful.\033[0m\n'
