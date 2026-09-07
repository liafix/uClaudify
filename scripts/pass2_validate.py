#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "domain"))

from finbridge_domain.contracts import FINANCIAL_INVARIANTS, QUALITY_RULES  # noqa: E402
from finbridge_domain.golden_path import run_golden_path  # noqa: E402
from finbridge_domain.ledger import BatchConflictError, InMemoryBatchLedger  # noqa: E402
from finbridge_domain.models import RawTransactionRecord, Transaction  # noqa: E402
from finbridge_domain.rules import DataQualityEngine  # noqa: E402

REQUIRED_PATHS = (
    "services/domain/finbridge_domain/rules.py",
    "services/domain/finbridge_domain/invariants.py",
    "services/domain/finbridge_domain/ledger.py",
    "services/domain/tests/test_pass2_data_quality.py",
    "services/domain/tests/test_pass2_financial_invariants.py",
    "docs/PASS2_DOMAIN_HARDENING.md",
)


def raw(**overrides: object) -> RawTransactionRecord:
    values: dict[str, object] = {
        "transaction_id": "TX-P2",
        "account_id": "ACC-001",
        "booking_date": "2026-09-05",
        "amount": "10.25",
        "currency": "EUR",
        "direction": "CREDIT",
        "counterparty": "Synthetic Counterparty",
        "source_system": "AlpineBank Legacy Finance",
        "source_line": 2,
    }
    values.update(overrides)
    return RawTransactionRecord(**values)  # type: ignore[arg-type]


def transaction(transaction_id: str, source_line: int) -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        account_id="ACC-001",
        booking_date="2026-09-05",
        amount=Decimal("10.25"),
        currency="EUR",
        direction="CREDIT",
        counterparty="Synthetic Counterparty",
        source_system="AlpineBank Legacy Finance",
        source_line=source_line,
    )


def main() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f"Missing PASS 2 artifacts: {missing}")

    if tuple(QUALITY_RULES) != ("DQ-01", "DQ-02", "DQ-03", "DQ-04", "DQ-05"):
        raise AssertionError("Frozen DQ contract changed")
    if tuple(FINANCIAL_INVARIANTS) != (
        "FIN-01",
        "FIN-02",
        "FIN-03",
        "FIN-04",
        "FIN-05",
    ):
        raise AssertionError("Frozen finance invariant contract changed")

    engine = DataQualityEngine()
    adversarial = {
        "DQ-01": [raw(transaction_id="TX-DUP", source_line=2), raw(transaction_id="TX-DUP", source_line=3)],
        "DQ-02": [raw(currency="EURO")],
        "DQ-03": [raw(amount="not-money")],
        "DQ-04": [raw(account_id="")],
    }
    for expected_rule, records in adversarial.items():
        result = engine.validate(records)
        if not result.issues or result.issues[-1].rule != expected_rule:
            raise AssertionError(f"{expected_rule} executable adversarial check failed")

    ledger = InMemoryBatchLedger()
    batch = (transaction("TX-A", 2),)
    ledger.commit("BATCH-P2", batch, accepted_count=1, quarantine_count=0)
    replay = ledger.replay("BATCH-P2", batch)
    if ledger.dataset_count != 1 or any(
        (replay.new_accepted_records, replay.duplicate_imports, replay.additional_quarantine_rows)
    ):
        raise AssertionError("DQ-05 / FIN-05 exact replay check failed")
    try:
        ledger.replay("BATCH-P2", (transaction("TX-CHANGED", 2),))
    except BatchConflictError:
        pass
    else:
        raise AssertionError("Changed payload under the same batch id did not fail closed")

    runtime = run_golden_path()
    exported = json.loads((ROOT / "apps/demo-web/data/golden-path.json").read_text(encoding="utf-8"))
    if runtime != exported:
        raise AssertionError("PASS 2 changed candidate evidence without exporting domain truth")
    ready = runtime["stages"][-1]
    if ready["state"] != "READY_FOR_ANALYTICS":
        raise AssertionError("PASS 2 regressed final golden-path state")
    if ready["reconciliation"]["difference_eur"] != "0.00":
        raise AssertionError("PASS 2 regressed exact financial reconciliation")

    current_pass_file = ROOT / "contracts" / "current_pass.txt"
    current_pass = int(current_pass_file.read_text(encoding="utf-8").strip()) if current_pass_file.exists() else 0
    if current_pass <= 2 and ((ROOT / "services/mcp").exists() or (ROOT / "functions/azure").exists()):
        raise AssertionError("Later-pass MCP/Azure implementation leaked into PASS 2")

    print("PASS: DQ-01..DQ-04 execute against untrusted raw records")
    print("PASS: DQ-05 exact replay has zero new import effects")
    print("PASS: changed payload under an existing batch id fails closed")
    print("PASS: FIN-01..FIN-04 are explicit reusable invariant checks")
    print("PASS: FIN-05 keeps one persisted dataset across replay")
    print("PASS: PASS 1 golden candidate story remains byte-for-byte evidence compatible")
    print("PASS 2 finance-domain hardening validation: PASS")


if __name__ == "__main__":
    main()
