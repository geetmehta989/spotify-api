#!/usr/bin/env bash
set -euo pipefail

# Activate local venv if present
if [[ -d .venv ]]; then
  source .venv/bin/activate
fi

export PYTHONPATH="$(pwd)"
python -m src.main "$@"
