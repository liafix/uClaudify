#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp:$ROOT/functions/azure"

python3 -m unittest discover -s "$ROOT/services/domain/tests" -p 'test_*.py' -v
python3 -m unittest discover -s "$ROOT/services/storage/tests" -p 'test_*.py' -v
python3 -m unittest discover -s "$ROOT/services/processing/tests" -p 'test_*.py' -v
python3 -m unittest discover -s "$ROOT/services/mcp/tests" -p 'test_*.py' -v
python3 -m compileall -q "$ROOT/services" "$ROOT/functions" "$ROOT/scripts"

for tool in ruff mypy; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "BLOCKED_TOOLCHAIN: $tool is required for the PASS 8 Python static gate" >&2
    exit 2
  fi
done
ruff check "$ROOT/services" "$ROOT/functions" "$ROOT/scripts"
mypy --config-file "$ROOT/pyproject.toml" \
  "$ROOT/services/domain/finbridge_domain" \
  "$ROOT/services/processing/finbridge_processing" \
  "$ROOT/services/mcp/finbridge_mcp"
echo "PASS 8 PYTHON GATE: GREEN"
