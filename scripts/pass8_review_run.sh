#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
LOG="${1:-PASS8_FINAL_REGRESSION_2026-09-07.log}"
: > "$LOG"

pass=0
blocked=0
failed=0

run_gate() {
  local name="$1"; shift
  {
    echo
    echo "===== $name ====="
    "$@"
  } >>"$LOG" 2>&1
  local rc=$?
  if [[ $rc -eq 0 ]]; then
    echo "RESULT $name: PASS" | tee -a "$LOG"
    pass=$((pass+1))
  elif [[ $rc -eq 2 || $rc -eq 124 ]]; then
    echo "RESULT $name: BLOCKED (exit=$rc)" | tee -a "$LOG"
    blocked=$((blocked+1))
  else
    echo "RESULT $name: FAIL (exit=$rc)" | tee -a "$LOG"
    failed=$((failed+1))
  fi
}

run_gate "STRUCTURAL" python3 scripts/pass8_validate.py
run_gate "PRIOR_PASS_CONTRACTS" ./scripts/pass8_prior_contracts_gate.sh
run_gate "PASS7_REGRESSION" ./scripts/pass7_gate.sh
run_gate "GOLDEN_PATH" python3 scripts/pass8_golden_regression.py
run_gate "JAVA" ./scripts/test_java.sh
run_gate "PYTHON_STATIC_FULL" ./scripts/pass8_python_gate.sh
run_gate "FRONTEND_FULL" ./scripts/pass8_frontend_gate.sh
run_gate "TERRAFORM" ./scripts/pass8_terraform_gate.sh
run_gate "MCP_OFFICIAL_SDK" ./scripts/pass8_mcp_sdk_gate.sh
run_gate "SECRET_CREDENTIAL_SCAN" python3 scripts/pass8_security_scan.py
run_gate "DEPENDENCY_VULNERABILITY" ./scripts/pass8_dependency_audit.sh

{
  echo
  echo "PASS8_REVIEW_SUMMARY pass=$pass blocked=$blocked failed=$failed"
  if [[ $failed -gt 0 ]]; then
    echo "PASS8_REVIEW_VERDICT=FAIL"
  elif [[ $blocked -gt 0 ]]; then
    echo "PASS8_REVIEW_VERDICT=BLOCKED_EXTERNAL_OR_TOOLCHAIN"
  else
    echo "PASS8_REVIEW_VERDICT=GREEN"
  fi
} | tee -a "$LOG"

[[ $failed -eq 0 && $blocked -eq 0 ]]
