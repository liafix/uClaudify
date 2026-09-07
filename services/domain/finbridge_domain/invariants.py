"""Executable FIN-01..FIN-04 finance invariants.

FIN-05 is a persisted-dataset replay invariant and is enforced by the batch ledger. Keeping these
checks independent from UI/cloud concerns lets tests prove the finance contract directly.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Iterable

from .models import ReconciliationResult, Transaction


class FinancialInvariantError(AssertionError):
    """Raised when a frozen finance invariant is violated."""


def assert_fin_01_accepted_once(accepted: Iterable[Transaction]) -> None:
    rows = tuple(accepted)
    source_lines = [row.source_line for row in rows]
    if len(source_lines) != len(set(source_lines)):
        raise FinancialInvariantError("FIN-01 violated: accepted source row counted more than once")


def assert_fin_02_no_duplicate_verified(accepted: Iterable[Transaction]) -> None:
    rows = tuple(accepted)
    transaction_ids = [row.transaction_id for row in rows]
    if len(transaction_ids) != len(set(transaction_ids)):
        raise FinancialInvariantError("FIN-02 violated: duplicate transaction entered verified data")


def assert_fin_03_record_accountability(
    batch: Iterable[Transaction],
    accepted: Iterable[Transaction],
    quarantined: Iterable[Transaction],
) -> None:
    batch_lines = {row.source_line for row in batch}
    accepted_lines = {row.source_line for row in accepted}
    quarantined_lines = {row.source_line for row in quarantined}
    if accepted_lines & quarantined_lines:
        raise FinancialInvariantError("FIN-03 violated: a source row has multiple outcomes")
    if accepted_lines | quarantined_lines != batch_lines:
        raise FinancialInvariantError("FIN-03 violated: source rows are missing an outcome")


def reconcile_accepted_records(
    accepted: Iterable[Transaction],
    *,
    opening_balance_eur: Decimal,
    expected_closing_balance_eur: Decimal,
) -> ReconciliationResult:
    rows = tuple(accepted)
    credits = sum(
        (row.amount for row in rows if row.direction == "CREDIT"),
        start=Decimal("0.00"),
    )
    debits = sum(
        (row.amount for row in rows if row.direction == "DEBIT"),
        start=Decimal("0.00"),
    )
    calculated = opening_balance_eur + credits - debits
    return ReconciliationResult(
        opening_balance_eur=opening_balance_eur,
        credits_eur=credits,
        debits_eur=debits,
        expected_closing_balance_eur=expected_closing_balance_eur,
        calculated_closing_balance_eur=calculated,
    )


def assert_fin_04_reconciliation_from_accepted(
    accepted: Iterable[Transaction],
    result: ReconciliationResult,
) -> None:
    recomputed = reconcile_accepted_records(
        accepted,
        opening_balance_eur=result.opening_balance_eur,
        expected_closing_balance_eur=result.expected_closing_balance_eur,
    )
    if recomputed != result:
        raise FinancialInvariantError(
            "FIN-04 violated: reconciliation includes data outside accepted records"
        )
