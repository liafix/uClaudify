#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/apps/demo-web"

if [[ -x node_modules/.bin/tsc && -d node_modules/react ]]; then
  ./node_modules/.bin/tsc --noEmit -p tsconfig.json
else
  echo "Frontend dependencies unavailable; using PASS 1 fallback declaration check."
  tsc --noEmit -p tsconfig.fallback.json
fi

node scripts/contract-check.mjs
