#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp:$ROOT/functions/azure"

echo "== FinBridge PASS 6 deterministic regression gate =="
python3 "$ROOT/scripts/pass0_validate.py"
PYTHONPATH="$ROOT/services/domain" python3 "$ROOT/scripts/export_pass1_demo.py"
python3 "$ROOT/scripts/pass1_validate.py"
python3 "$ROOT/scripts/pass2_validate.py"
python3 "$ROOT/scripts/pass3_validate.py"
python3 "$ROOT/scripts/pass4_validate.py"
PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp" \
  python3 "$ROOT/scripts/export_pass5_evidence.py"
python3 "$ROOT/scripts/pass5_validate.py"
python3 "$ROOT/scripts/pass6_validate.py"

python3 -m unittest discover -s "$ROOT/services/domain/tests" -p 'test_*.py' -v
python3 -m unittest discover -s "$ROOT/services/storage/tests" -p 'test_*.py' -v
python3 -m unittest discover -s "$ROOT/services/processing/tests" -p 'test_*.py' -v
python3 -m unittest discover -s "$ROOT/services/mcp/tests" -p 'test_*.py' -v

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

echo "PASS 6 DETERMINISTIC GATE: GREEN"
