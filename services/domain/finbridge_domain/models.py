"""Framework-free finance-domain models for the FinBridge candidate demo.

PASS 2 adds an explicit raw-record boundary so malformed legacy values can be tested before they
become trusted canonical :class:`Transaction` objects. No cloud or persistence framework types leak
into this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from .contracts import GoldenState

Direction = Literal["CREDIT", "DEBIT"]


@dataclass(frozen=True, slots=True)
class RawTransactionRecord:
    """Untrusted legacy-shaped record accepted by the data-quality boundary.

    `amount` is intentionally `object`: PASS 2 must prove that malformed monetary values are rejected
    at runtime instead of assuming Python type hints have already made them safe.
    """

    transaction_id: str | None
    account_id: str | None
    booking_date: str | None
    amount: object
    currency: str | None
    direction: str | None
    counterparty: str | None
    source_system: str | None
    source_line: int


@dataclass(frozen=True, slots=True)
class Transaction:
    transaction_id: str
    account_id: str
    booking_date: str
    amount: Decimal
    currency: str
    direction: Direction
    counterparty: str
    source_system: str
    source_line: int


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    transaction_id: str
    source_line: int
    rule: str
    reason: str


@dataclass(frozen=True, slots=True)
class ValidationResult:
    accepted: tuple[Transaction, ...]
    issues: tuple[ValidationIssue, ...]


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    opening_balance_eur: Decimal
    credits_eur: Decimal
    debits_eur: Decimal
    expected_closing_balance_eur: Decimal
    calculated_closing_balance_eur: Decimal

    @property
    def difference_eur(self) -> Decimal:
        return self.calculated_closing_balance_eur - self.expected_closing_balance_eur

    @property
    def reconciled(self) -> bool:
        return self.difference_eur == Decimal("0.00")


@dataclass(frozen=True, slots=True)
class ReplayResult:
    batch_id: str
    previously_processed: bool
    new_accepted_records: int
    duplicate_imports: int
    additional_quarantine_rows: int


@dataclass(frozen=True, slots=True)
class PipelineSnapshot:
    state: GoldenState
    input_records: int
    accepted_records: int
    anomaly_records: int
    quarantined_records: int
    unaccounted_records: int
    issues: tuple[ValidationIssue, ...]
    reconciliation: ReconciliationResult | None = None
    replay: ReplayResult | None = None
