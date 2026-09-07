#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== FinBridge PASS 5 gate =="
python3 "$ROOT/scripts/pass0_validate.py"
PYTHONPATH="$ROOT/services/domain" python3 "$ROOT/scripts/export_pass1_demo.py"
python3 "$ROOT/scripts/pass1_validate.py"
python3 "$ROOT/scripts/pass2_validate.py"
python3 "$ROOT/scripts/pass3_validate.py"
python3 "$ROOT/scripts/pass4_validate.py"
PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp" \
  python3 "$ROOT/scripts/export_pass5_evidence.py"
python3 "$ROOT/scripts/pass5_validate.py"
"$ROOT/scripts/test_python.sh"
"$ROOT/scripts/test_java.sh"
"$ROOT/scripts/typecheck_frontend.sh"
PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp" \
  python3 "$ROOT/scripts/pass5_mcp_stdio_smoke.py"
python3 -m compileall -q \
  "$ROOT/services/domain/finbridge_domain" \
  "$ROOT/services/storage/finbridge_storage" \
  "$ROOT/services/processing/finbridge_processing" \
  "$ROOT/services/mcp/finbridge_mcp" \
  "$ROOT/functions/azure"

echo "PASS 5 GATE: GREEN"
