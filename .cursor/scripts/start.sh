#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
mkdir -p data

if [[ ! -d .venv ]]; then
  bash .cursor/scripts/install.sh
fi

. .venv/bin/activate
python -m aaaradius.db init
