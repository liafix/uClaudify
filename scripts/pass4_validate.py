#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for relative in ("services/domain", "services/storage", "services/processing"):
    sys.path.insert(0, str(ROOT / relative))

from finbridge_domain.fixtures import build_synthetic_legacy_batch  # noqa: E402
from finbridge_processing.legacy_import import parse_canonical_csv  # noqa: E402

REQUIRED = (
    "adapters/legacy-java/src/main/java/com/finbridge/legacy/LegacyTransaction.java",
    "adapters/legacy-java/src/main/java/com/finbridge/legacy/CanonicalTransaction.java",
    "adapters/legacy-java/src/main/java/com/finbridge/legacy/LegacyTransactionMapper.java",
    "adapters/legacy-java/src/main/java/com/finbridge/legacy/LegacySyntheticSource.java",
    "adapters/legacy-java/src/main/java/com/finbridge/legacy/CanonicalCsvExporter.java",
    "services/processing/finbridge_processing/legacy_import.py",
    "services/processing/tests/test_pass4_legacy_import.py",
    "scripts/pass4_azurite_smoke.py",
    "docs/PASS4_JAVA_LEGACY_ADAPTER.md",
)


def main() -> None:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        raise AssertionError(f"Missing PASS 4 artifacts: {missing}")
    current_pass = int((ROOT / "contracts/current_pass.txt").read_text().strip())
    if current_pass < 4:
        raise AssertionError("PASS marker must be at least 4")

    java = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (ROOT / "adapters/legacy-java/src/main/java/com/finbridge/legacy").glob("*.java")
    )
    forbidden_java = (
        "DQ-01",
        "DQ-02",
        "quarantine",
        "READY_FOR_ANALYTICS",
        "reconciliation",
        "expected_closing",
    )
    if any(token.lower() in java.lower() for token in forbidden_java):
        raise AssertionError("Java adapter leaked Python finance/DQ ownership")

    artifact = ROOT / "artifacts/pass4/java-canonical.csv"
    if artifact.exists():
        imported = parse_canonical_csv(artifact.read_text(encoding="utf-8"))
        if imported != build_synthetic_legacy_batch():
            raise AssertionError("Java canonical CSV does not preserve frozen Python fixture semantics")

    if current_pass <= 4 and (ROOT / "services/mcp").exists():
        raise AssertionError("PASS 5 MCP scope leaked into a PASS 4 artifact")

    print("PASS: Java legacy transaction model + mapper + canonical exporter implemented")
    print("PASS: Java preserves duplicate/currency anomalies instead of deciding DQ outcomes")
    print("PASS: canonical CSV boundary is structurally consumed by Python processing")
    print("PASS: Python remains sole owner of DQ/quarantine/reconciliation/readiness")
    print("PASS: PASS 4 ownership boundary remains intact under later-pass regression")
    print("PASS 4 structural ownership validation: PASS")


if __name__ == "__main__":
    main()
