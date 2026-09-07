"""PASS 4 canonical CSV import boundary for the Java legacy adapter.

This module performs transport/schema parsing only. DQ, quarantine, reconciliation and readiness
remain owned by the existing Python domain engine.
"""

from __future__ import annotations

import csv
from decimal import Decimal
from io import StringIO
from pathlib import Path

from finbridge_domain.contracts import CANONICAL_TRANSACTION_FIELDS
from finbridge_domain.models import Transaction


class LegacyImportError(ValueError):
    """Raised when the structural Java->Python transport contract is invalid."""


def parse_canonical_csv(text: str) -> tuple[Transaction, ...]:
    reader = csv.DictReader(StringIO(text, newline=""))
    if reader.fieldnames != list(CANONICAL_TRANSACTION_FIELDS):
        raise LegacyImportError(
            f"Canonical CSV header mismatch: expected {list(CANONICAL_TRANSACTION_FIELDS)!r}, "
            f"got {reader.fieldnames!r}"
        )

    rows: list[Transaction] = []
    for row in reader:
        if None in row:
            raise LegacyImportError(f"Unexpected extra columns at source line {reader.line_num}")
        try:
            amount = Decimal(row["amount"])
            direction = row["direction"]
            if direction not in {"CREDIT", "DEBIT"}:
                raise LegacyImportError(
                    f"Unsupported canonical direction at source line {reader.line_num}: {direction}"
                )
            rows.append(
                Transaction(
                    transaction_id=row["transaction_id"],
                    account_id=row["account_id"],
                    booking_date=row["booking_date"],
                    amount=amount,
                    currency=row["currency"],
                    direction=direction,  # type: ignore[arg-type]
                    counterparty=row["counterparty"],
                    source_system=row["source_system"],
                    source_line=reader.line_num,
                )
            )
        except (ArithmeticError, KeyError) as exc:
            raise LegacyImportError(f"Malformed canonical row at source line {reader.line_num}") from exc
    return tuple(rows)


def load_canonical_csv(path: str | Path) -> tuple[Transaction, ...]:
    return parse_canonical_csv(Path(path).read_text(encoding="utf-8"))
