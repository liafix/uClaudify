"""Deterministic AlpineBank fixture generator for PASS 1.

The generator creates exactly the frozen scenario without storing 1,024 hand-authored rows. The
output is deterministic and contains no real person, bank, account or client data.
"""

from __future__ import annotations

from decimal import Decimal

from .contracts import FROZEN_SCENARIO
from .models import Transaction

VALID_CURRENCIES: frozenset[str] = frozenset({"EUR", "USD", "GBP", "CHF"})


def _accepted_transaction_ids() -> list[int]:
    # Reserve 1011 and 1012 for the two invalid-currency rows while preserving 1,019 accepted rows.
    ids = [value for value in range(1, 1022) if value not in {1011, 1012}]
    if len(ids) != FROZEN_SCENARIO.accepted_records:
        raise AssertionError("Synthetic accepted-id generator no longer matches the frozen contract")
    return ids


def build_synthetic_legacy_batch() -> tuple[Transaction, ...]:
    """Return the exact 1,024-row frozen synthetic legacy batch."""

    rows: list[Transaction] = []
    accepted_ids = _accepted_transaction_ids()

    # 509 credits: 508 x 200.00 + 1 x 23,800.00 = 125,400.00
    credit_ids = accepted_ids[:509]
    for index, numeric_id in enumerate(credit_ids):
        amount = Decimal("23800.00") if index == 508 else Decimal("200.00")
        rows.append(
            Transaction(
                transaction_id=f"TX-{numeric_id:05d}",
                account_id=f"ACC-{(numeric_id % 17) + 1:03d}",
                booking_date="2026-09-05",
                amount=amount,
                currency="EUR",
                direction="CREDIT",
                counterparty=f"Synthetic Counterparty {numeric_id:04d}",
                source_system=FROZEN_SCENARIO.source_system,
                source_line=len(rows) + 2,
            )
        )

    # 510 debits: 509 x 150.00 + 1 x 22,350.00 = 98,700.00
    debit_ids = accepted_ids[509:]
    for index, numeric_id in enumerate(debit_ids):
        amount = Decimal("22350.00") if index == 509 else Decimal("150.00")
        rows.append(
            Transaction(
                transaction_id=f"TX-{numeric_id:05d}",
                account_id=f"ACC-{(numeric_id % 17) + 1:03d}",
                booking_date="2026-09-05",
                amount=amount,
                currency="EUR",
                direction="DEBIT",
                counterparty=f"Synthetic Counterparty {numeric_id:04d}",
                source_system=FROZEN_SCENARIO.source_system,
                source_line=len(rows) + 2,
            )
        )

    by_id = {row.transaction_id: row for row in rows}
    for duplicate_id in ("TX-00482", "TX-00791", "TX-00902"):
        original = by_id[duplicate_id]
        rows.append(
            Transaction(
                transaction_id=original.transaction_id,
                account_id=original.account_id,
                booking_date=original.booking_date,
                amount=original.amount,
                currency=original.currency,
                direction=original.direction,
                counterparty=original.counterparty,
                source_system=original.source_system,
                source_line=len(rows) + 2,
            )
        )

    rows.extend(
        [
            Transaction(
                transaction_id="TX-01011",
                account_id="ACC-011",
                booking_date="2026-09-05",
                amount=Decimal("10.00"),
                currency="EUX",
                direction="CREDIT",
                counterparty="Synthetic Invalid Currency A",
                source_system=FROZEN_SCENARIO.source_system,
                source_line=len(rows) + 2,
            ),
            Transaction(
                transaction_id="TX-01012",
                account_id="ACC-012",
                booking_date="2026-09-05",
                amount=Decimal("20.00"),
                currency="EURO",
                direction="DEBIT",
                counterparty="Synthetic Invalid Currency B",
                source_system=FROZEN_SCENARIO.source_system,
                source_line=len(rows) + 3,
            ),
        ]
    )

    if len(rows) != FROZEN_SCENARIO.input_records:
        raise AssertionError(f"Synthetic batch has {len(rows)} rows instead of 1,024")
    return tuple(rows)
