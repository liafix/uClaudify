#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 scripts/pass0_validate.py
PYTHONPATH=services/domain python3 scripts/export_pass1_demo.py
python3 scripts/pass1_validate.py
python3 scripts/pass2_validate.py
python3 scripts/pass3_validate.py
python3 scripts/pass4_validate.py
PYTHONPATH=services/domain:services/storage:services/processing:services/mcp python3 scripts/export_pass5_evidence.py
python3 scripts/pass5_validate.py
echo "PASS 8 PRIOR PASS 0-5 CONTRACT REGRESSION: GREEN"
