#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v pip-audit >/dev/null 2>&1; then
  echo "BLOCKED_TOOLCHAIN: pip-audit is required" >&2
  exit 2
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "BLOCKED_TOOLCHAIN: npm is required" >&2
  exit 2
fi

pip-audit -r "$ROOT/requirements-pass8.txt" --progress-spinner off
(
  cd "$ROOT/apps/demo-web"
  test -d node_modules || { echo "BLOCKED_PREREQUISITE: frontend clean install must run before npm audit" >&2; exit 2; }
  npm audit --audit-level=low
)
echo "PASS 8 DEPENDENCY VULNERABILITY GATE: GREEN (0 known vulnerabilities accepted; fail threshold=LOW)"
