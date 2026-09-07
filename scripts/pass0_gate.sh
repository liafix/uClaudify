#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== FinBridge PASS 0 gate =="
python3 "$ROOT/scripts/pass0_validate.py"
"$ROOT/scripts/test_python.sh"
"$ROOT/scripts/test_java.sh"
"$ROOT/scripts/typecheck_frontend.sh"

echo "PASS 0 GATE: GREEN"
