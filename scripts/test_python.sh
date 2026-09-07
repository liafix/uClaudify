#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/services/domain:$ROOT/services/storage:$ROOT/services/processing:$ROOT/services/mcp:$ROOT/functions/azure"
python3 -m unittest discover -s "$ROOT/services/domain/tests" -p 'test_*.py' -v
if [[ -d "$ROOT/services/storage/tests" ]]; then
  python3 -m unittest discover -s "$ROOT/services/storage/tests" -p 'test_*.py' -v
fi
if [[ -d "$ROOT/services/processing/tests" ]]; then
  python3 -m unittest discover -s "$ROOT/services/processing/tests" -p 'test_*.py' -v
fi
if [[ -d "$ROOT/services/mcp/tests" ]]; then
  python3 -m unittest discover -s "$ROOT/services/mcp/tests" -p 'test_*.py' -v
fi
