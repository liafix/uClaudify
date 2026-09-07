#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mapfile -t MAIN < <(find "$ROOT/adapters/legacy-java/src/main/java" -name '*.java' -type f | sort)
mapfile -t TEST < <(find "$ROOT/adapters/legacy-java/src/test/java" -name '*.java' -type f | sort)
javac -d "$TMP" "${MAIN[@]}" "${TEST[@]}"
java -cp "$TMP" com.finbridge.legacy.LegacyAdapterContractTest
java -cp "$TMP" com.finbridge.legacy.LegacyAdapterPass4Test
java -cp "$TMP" com.finbridge.legacy.LegacyAdapterApp "$TMP/java-canonical.csv" >/dev/null
python3 "$ROOT/scripts/pass4_java_python_storage_smoke.py" "$TMP/java-canonical.csv"
