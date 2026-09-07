#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "domain"))

from finbridge_domain.golden_path import run_golden_path  # noqa: E402

REQUIRED_PATHS = (
    "services/domain/finbridge_domain/models.py",
    "services/domain/finbridge_domain/fixtures.py",
    "services/domain/finbridge_domain/pipeline.py",
    "services/domain/finbridge_domain/golden_path.py",
    "services/domain/tests/test_pass1_golden_path.py",
    "apps/demo-web/components/golden-demo.tsx",
    "apps/demo-web/data/golden-path.json",
    "apps/demo-web/app/globals.css",
)


def main() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f"Missing PASS 1 artifacts: {missing}")

    runtime = run_golden_path()
    exported = json.loads((ROOT / "apps/demo-web/data/golden-path.json").read_text(encoding="utf-8"))
    if runtime != exported:
        raise AssertionError("Committed frontend evidence does not match the Python domain engine")

    expected_history = [
        "RECEIVED",
        "INGESTION_PASS",
        "SCHEMA_PASS",
        "NORMALIZATION_PASS",
        "QUALITY_BLOCKED",
        "QUARANTINED",
        "RECONCILED",
        "IDEMPOTENCY_PASS",
        "READY_FOR_ANALYTICS",
    ]
    if runtime["state_history"] != expected_history:
        raise AssertionError("Golden state history changed")

    blocked = runtime["stages"][1]
    ready = runtime["stages"][-1]
    if (blocked["accepted_records"], blocked["anomaly_records"]) != (1019, 5):
        raise AssertionError("Quality gate evidence changed")
    if ready["unaccounted_records"] != 0:
        raise AssertionError("Final record accountability is not 100%")
    if ready["reconciliation"]["difference_eur"] != "0.00":
        raise AssertionError("Financial reconciliation is not exact")
    if any(
        ready["replay"][key] != 0
        for key in ("new_accepted_records", "duplicate_imports", "additional_quarantine_rows")
    ):
        raise AssertionError("Replay is not idempotent")

    current_pass_file = ROOT / "contracts" / "current_pass.txt"
    current_pass = int(current_pass_file.read_text(encoding="utf-8").strip()) if current_pass_file.exists() else 0
    if current_pass <= 1 and ((ROOT / "services/mcp").exists() or (ROOT / "functions/azure").exists()):
        raise AssertionError("PASS 5/3 implementation leaked into PASS 1")

    print("PASS: executable Python golden path")
    print("PASS: frontend evidence derived from Python domain truth")
    print("PASS: 1,024 -> 1,019 + 5 quarantine -> 0 unaccounted")
    print("PASS: exact €0.00 reconciliation difference")
    print("PASS: replay creates 0 new imports")
    print("PASS 1 vertical-slice validation: PASS")


if __name__ == "__main__":
    main()
