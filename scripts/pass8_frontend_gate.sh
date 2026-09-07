#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB="$ROOT/apps/demo-web"
cd "$WEB"

node scripts/contract-check.mjs
if ! command -v npm >/dev/null 2>&1; then
  echo "BLOCKED_TOOLCHAIN: npm is required" >&2
  exit 2
fi
if ! npm_config_fetch_retries=0 npm_config_fetch_timeout=5000 npm ping --silent >/dev/null 2>&1; then
  echo "BLOCKED_NETWORK: npm registry is not reachable for the required clean install/build/audit path" >&2
  exit 2
fi
rm -rf node_modules .next package-lock.json
npm install --package-lock-only --ignore-scripts --no-audit --no-fund
npm ci --no-audit --no-fund
npm run contract
npm run typecheck
npm run build

node - <<'NODE'
const fs = require("node:fs");
const manifest = JSON.parse(fs.readFileSync(".next/server/app-paths-manifest.json", "utf8"));
for (const key of ["/page", "/quality/page", "/operations/page", "/architecture/page", "/candidate/page"]) {
  if (!(key in manifest)) throw new Error(`optimized build route missing from app-paths manifest: ${key}`);
}
console.log("PASS: optimized production build contains all five candidate routes");
NODE

grep -Rqi 'noindex' .next/server/app || { echo "ERROR: built output lacks noindex evidence" >&2; exit 1; }
grep -Rqi 'AlpineBank is fictional' .next/server/app || { echo "ERROR: built output lacks synthetic disclaimer" >&2; exit 1; }
echo "PASS 8 FRONTEND GATE: GREEN"
