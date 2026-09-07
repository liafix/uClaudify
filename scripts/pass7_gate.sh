#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/pass7_validate.py
(
  cd apps/demo-web
  node scripts/contract-check.mjs
  if command -v tsc >/dev/null 2>&1; then
    tsc --noEmit -p tsconfig.fallback.json
  fi
)
PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp:$ROOT/functions/azure" python3 -m unittest discover -s services/domain/tests -p 'test_*.py'
PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp:$ROOT/functions/azure" python3 -m unittest discover -s services/storage/tests -p 'test_*.py'
PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp:$ROOT/functions/azure" python3 -m unittest discover -s services/processing/tests -p 'test_*.py'
PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp:$ROOT/functions/azure" python3 -m unittest discover -s services/mcp/tests -p 'test_*.py'
PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing" python3 scripts/pass4_java_python_storage_smoke.py artifacts/pass4/java-canonical.csv
PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp:$ROOT/functions/azure" python3 scripts/pass5_mcp_stdio_smoke.py
python3 -m compileall -q services functions scripts
printf 'PASS 7 RECONSTITUTED HANDOFF GATE: GREEN\n'
