#!/usr/bin/env bash
set -euo pipefail

if ! command -v python >/dev/null 2>&1; then
  echo "Python 3.10+ is required" >&2
  exit 1
fi

python -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip
if [[ "${1:-}" == "dev" ]]; then
  python -m pip install -e '.[dev]'
  pre-commit install
else
  python -m pip install -e .
fi
mkdir -p conversations logs
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Edit .env with your OpenAI API key."
fi
echo "Setup complete. Activate venv and run: ai-agent chat"
