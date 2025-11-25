#!/usr/bin/env bash
# Small helper for Unix-like shells to activate the repo venv and run Streamlit.
# Usage: ./run.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV="$ROOT/.venv/bin/activate"

if [ -f "$VENV" ]; then
  # shellcheck disable=SC1090
  source "$VENV"
else
  echo "No .venv found; create one with: python -m venv .venv && pip install -r requirements.txt"
fi

if command -v streamlit >/dev/null 2>&1; then
  streamlit run app.py
else
  python -m streamlit run app.py
fi
