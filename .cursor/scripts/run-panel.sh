#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

if [[ ! -d .venv ]]; then
  bash .cursor/scripts/install.sh
fi

. .venv/bin/activate
python -m aaaradius.db init
exec uvicorn aaaradius.main:app --host 0.0.0.0 --port 8080 --reload
