#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

printf '== FinBridge PASS 8 full production-hardening gate ==\n'
python3 scripts/pass8_validate.py
./scripts/pass8_prior_contracts_gate.sh
python3 scripts/pass8_golden_regression.py
./scripts/test_java.sh
./scripts/pass8_python_gate.sh
./scripts/pass8_frontend_gate.sh
./scripts/pass8_terraform_gate.sh
./scripts/pass8_mcp_sdk_gate.sh
python3 scripts/pass8_security_scan.py
./scripts/pass8_dependency_audit.sh
printf 'PASS 8 FULL PRODUCTION-HARDENING GATE: GREEN\n'
