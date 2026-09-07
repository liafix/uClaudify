#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp:$ROOT/functions/azure"
python3 -m unittest discover -s "$ROOT/services/mcp/tests" -p 'test_*.py' -v
python3 "$ROOT/scripts/pass5_mcp_stdio_smoke.py"
python3 - <<'PY'
try:
    import mcp  # noqa: F401
except Exception as exc:
    import sys
    print(f"BLOCKED_TOOLCHAIN: official mcp Python SDK v2 is required: {exc}", file=sys.stderr)
    raise SystemExit(2)
PY
python3 "$ROOT/scripts/pass5_official_sdk_smoke.py"
echo "PASS 8 MCP GATE: GREEN"
