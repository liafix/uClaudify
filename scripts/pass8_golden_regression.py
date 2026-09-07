#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "domain"))

from finbridge_domain.golden_path import run_golden_path  # noqa: E402

EXPECTED = {
    "batch_id": "2026-09-05-001",
    "input": 1024,
    "accepted": 1019,
    "duplicates": 3,
    "invalid_currency": 2,
    "quarantined": 5,
    "unaccounted": 0,
    "opening": "1000000.00",
    "credits": "125400.00",
    "debits": "98700.00",
    "expected_closing": "1026700.00",
    "calculated_closing": "1026700.00",
    "difference": "0.00",
    "replay_new": 0,
    "replay_duplicates": 0,
    "replay_quarantine": 0,
    "final_state": "READY_FOR_ANALYTICS",
}


def main() -> None:
    runtime = run_golden_path()
    exported = json.loads((ROOT / "apps/demo-web/data/golden-path.json").read_text(encoding="utf-8"))
    if runtime != exported:
        raise AssertionError("Frontend golden-path evidence diverges from Python domain truth")
    if runtime["batch_id"] != EXPECTED["batch_id"]:
        raise AssertionError("Frozen batch id changed")

    blocked = next(stage for stage in runtime["stages"] if stage["state"] == "QUALITY_BLOCKED")
    quarantined = next(stage for stage in runtime["stages"] if stage["state"] == "QUARANTINED")
    ready = next(stage for stage in runtime["stages"] if stage["state"] == "READY_FOR_ANALYTICS")

    checks = {
        "input": blocked["input_records"],
        "accepted": blocked["accepted_records"],
        "quarantined": quarantined["quarantined_records"],
        "unaccounted": ready["unaccounted_records"],
        "opening": ready["reconciliation"]["opening_balance_eur"],
        "credits": ready["reconciliation"]["credits_eur"],
        "debits": ready["reconciliation"]["debits_eur"],
        "expected_closing": ready["reconciliation"]["expected_closing_balance_eur"],
        "calculated_closing": ready["reconciliation"]["calculated_closing_balance_eur"],
        "difference": ready["reconciliation"]["difference_eur"],
        "replay_new": ready["replay"]["new_accepted_records"],
        "replay_duplicates": ready["replay"]["duplicate_imports"],
        "replay_quarantine": ready["replay"]["additional_quarantine_rows"],
        "final_state": ready["state"],
    }
    for key, actual in checks.items():
        if actual != EXPECTED[key]:
            raise AssertionError(f"Frozen golden-path value changed: {key}={actual!r}")

    issues = blocked["issues"]
    dq01 = [issue for issue in issues if issue["rule"] == "DQ-01"]
    dq02 = [issue for issue in issues if issue["rule"] == "DQ-02"]
    if len(dq01) != EXPECTED["duplicates"] or len(dq02) != EXPECTED["invalid_currency"]:
        raise AssertionError("Frozen DQ-01/DQ-02 anomaly split changed")

    print("PASS 8 GOLDEN PATH REGRESSION: GREEN")
    print("batch=2026-09-05-001")
    print("input=1024 accepted=1019 dq01_duplicates=3 dq02_invalid_currency=2 quarantine=5 unaccounted=0")
    print("opening=€1,000,000.00 credits=€125,400.00 debits=€98,700.00")
    print("expected_closing=€1,026,700.00 calculated_closing=€1,026,700.00 difference=€0.00")
    print("replay=0/0/0 committed_dataset_count=1 final_state=READY_FOR_ANALYTICS")


if __name__ == "__main__":
    main()
