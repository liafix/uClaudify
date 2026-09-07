"""Executable DQ-01..DQ-04 data-quality rules.

DQ-05 is an import/retry property and is enforced by :mod:`finbridge_domain.ledger` rather than by
single-record validation. The engine emits at most one blocking issue per source row so record
accountability remains unambiguous and deterministic.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Iterable

from .fixtures import VALID_CURRENCIES
from .models import RawTransactionRecord, Transaction, ValidationIssue, ValidationResult

Record = Transaction | RawTransactionRecord
_REQUIRED_FIELDS = (
    "transaction_id",
    "account_id",
    "booking_date",
    "currency",
    "direction",
    "counterparty",
    "source_system",
)


def _display_transaction_id(record: Record) -> str:
    value = record.transaction_id
    return value.strip() if isinstance(value, str) and value.strip() else "<missing>"


def _required_field_issue(record: Record) -> ValidationIssue | None:
    for field in _REQUIRED_FIELDS:
        value = getattr(record, field)
        if not isinstance(value, str) or not value.strip():
            return ValidationIssue(
                transaction_id=_display_transaction_id(record),
                source_line=record.source_line,
                rule="DQ-04",
                reason=f"REQUIRED_FIELD_EMPTY:{field}",
            )
    return None


def _parse_amount(record: Record) -> tuple[Decimal | None, ValidationIssue | None]:
    value = record.amount
    if isinstance(value, bool) or isinstance(value, float):
        amount = None
    elif isinstance(value, Decimal):
        amount = value
    elif isinstance(value, str):
        try:
            amount = Decimal(value.strip()) if value.strip() else None
        except InvalidOperation:
            amount = None
    elif isinstance(value, int):
        amount = Decimal(value)
    else:
        amount = None

    if amount is None or not amount.is_finite():
        return None, ValidationIssue(
            transaction_id=_display_transaction_id(record),
            source_line=record.source_line,
            rule="DQ-03",
            reason="INVALID_AMOUNT",
        )
    return amount, None


def _normalize(record: Record, amount: Decimal) -> Transaction:
    # Required-field validation runs first, so these assertions are executable documentation of the
    # narrowing boundary and catch accidental rule-order regressions.
    assert isinstance(record.transaction_id, str)
    assert isinstance(record.account_id, str)
    assert isinstance(record.booking_date, str)
    assert isinstance(record.currency, str)
    assert isinstance(record.direction, str)
    assert isinstance(record.counterparty, str)
    assert isinstance(record.source_system, str)
    if record.direction not in {"CREDIT", "DEBIT"}:
        raise ValueError(f"Unsupported direction at source line {record.source_line}: {record.direction}")
    return Transaction(
        transaction_id=record.transaction_id.strip(),
        account_id=record.account_id.strip(),
        booking_date=record.booking_date.strip(),
        amount=amount,
        currency=record.currency.strip(),
        direction=record.direction,  # type: ignore[arg-type]
        counterparty=record.counterparty.strip(),
        source_system=record.source_system.strip(),
        source_line=record.source_line,
    )


class DataQualityEngine:
    """Validate untrusted records into canonical transactions using frozen DQ rules."""

    def validate(self, records: Iterable[Record]) -> ValidationResult:
        seen_transaction_ids: set[str] = set()
        accepted: list[Transaction] = []
        issues: list[ValidationIssue] = []

        for record in records:
            # DQ-04 runs before other field-dependent checks so missing values never become trusted
            # keys or currency values.
            required_issue = _required_field_issue(record)
            if required_issue is not None:
                issues.append(required_issue)
                continue

            amount, amount_issue = _parse_amount(record)
            if amount_issue is not None or amount is None:
                assert amount_issue is not None
                issues.append(amount_issue)
                continue

            assert isinstance(record.currency, str)
            if record.currency.strip() not in VALID_CURRENCIES:
                issues.append(
                    ValidationIssue(
                        transaction_id=_display_transaction_id(record),
                        source_line=record.source_line,
                        rule="DQ-02",
                        reason=f"INVALID_CURRENCY:{record.currency.strip()}",
                    )
                )
                continue

            assert isinstance(record.transaction_id, str)
            transaction_id = record.transaction_id.strip()
            if transaction_id in seen_transaction_ids:
                issues.append(
                    ValidationIssue(
                        transaction_id=transaction_id,
                        source_line=record.source_line,
                        rule="DQ-01",
                        reason="DUPLICATE_TRANSACTION",
                    )
                )
                continue

            canonical = _normalize(record, amount)
            accepted.append(canonical)
            seen_transaction_ids.add(canonical.transaction_id)

        return ValidationResult(accepted=tuple(accepted), issues=tuple(issues))
