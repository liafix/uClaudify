"""Deterministic JSON serialization for persisted candidate-demo evidence."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Iterable, Mapping

from finbridge_domain.ledger import CommittedBatch
from finbridge_domain.models import Transaction, ValidationIssue


def _json_bytes(payload: object) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode(
        "utf-8"
    )


def _load(data: bytes) -> Any:
    return json.loads(data.decode("utf-8"))


def transaction_to_dict(row: Transaction) -> dict[str, object]:
    return {
        "transaction_id": row.transaction_id,
        "account_id": row.account_id,
        "booking_date": row.booking_date,
        "amount": format(row.amount, "f"),
        "currency": row.currency,
        "direction": row.direction,
        "counterparty": row.counterparty,
        "source_system": row.source_system,
        "source_line": row.source_line,
    }


def transaction_from_dict(payload: Mapping[str, object]) -> Transaction:
    direction = str(payload["direction"])
    if direction not in {"CREDIT", "DEBIT"}:
        raise ValueError(f"Unsupported persisted direction: {direction}")
    return Transaction(
        transaction_id=str(payload["transaction_id"]),
        account_id=str(payload["account_id"]),
        booking_date=str(payload["booking_date"]),
        amount=Decimal(str(payload["amount"])),
        currency=str(payload["currency"]),
        direction=direction,  # type: ignore[arg-type]
        counterparty=str(payload["counterparty"]),
        source_system=str(payload["source_system"]),
        source_line=int(payload["source_line"]),
    )


def batch_to_bytes(batch_id: str, rows: Iterable[Transaction]) -> bytes:
    return _json_bytes(
        {"batch_id": batch_id, "records": [transaction_to_dict(row) for row in tuple(rows)]}
    )


def batch_from_bytes(data: bytes) -> tuple[str, tuple[Transaction, ...]]:
    payload = _load(data)
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise ValueError("Persisted batch payload has invalid shape")
    return str(payload["batch_id"]), tuple(transaction_from_dict(item) for item in payload["records"])


def issue_to_dict(issue: ValidationIssue) -> dict[str, object]:
    return {
        "transaction_id": issue.transaction_id,
        "source_line": issue.source_line,
        "rule": issue.rule,
        "reason": issue.reason,
    }


def issue_from_dict(payload: Mapping[str, object]) -> ValidationIssue:
    return ValidationIssue(
        transaction_id=str(payload["transaction_id"]),
        source_line=int(payload["source_line"]),
        rule=str(payload["rule"]),
        reason=str(payload["reason"]),
    )


def quarantine_to_bytes(
    batch_id: str,
    rows: Iterable[Transaction],
    issues: Iterable[ValidationIssue],
) -> bytes:
    return _json_bytes(
        {
            "batch_id": batch_id,
            "records": [transaction_to_dict(row) for row in tuple(rows)],
            "issues": [issue_to_dict(issue) for issue in tuple(issues)],
        }
    )


def quarantine_from_bytes(
    data: bytes,
) -> tuple[str, tuple[Transaction, ...], tuple[ValidationIssue, ...]]:
    payload = _load(data)
    if not isinstance(payload, dict):
        raise ValueError("Persisted quarantine payload has invalid shape")
    records = payload.get("records")
    issues = payload.get("issues")
    if not isinstance(records, list) or not isinstance(issues, list):
        raise ValueError("Persisted quarantine payload is missing records/issues")
    return (
        str(payload["batch_id"]),
        tuple(transaction_from_dict(item) for item in records),
        tuple(issue_from_dict(item) for item in issues),
    )


def audit_event_to_bytes(
    *, batch_id: str, event_id: str, event_type: str, payload: Mapping[str, object]
) -> bytes:
    return _json_bytes(
        {
            "batch_id": batch_id,
            "event_id": event_id,
            "event_type": event_type,
            "payload": dict(payload),
        }
    )


def audit_event_from_bytes(data: bytes) -> tuple[str, str, str, dict[str, object]]:
    payload = _load(data)
    if not isinstance(payload, dict) or not isinstance(payload.get("payload"), dict):
        raise ValueError("Persisted audit event has invalid shape")
    return (
        str(payload["batch_id"]),
        str(payload["event_id"]),
        str(payload["event_type"]),
        dict(payload["payload"]),
    )


def commit_to_bytes(commit: CommittedBatch) -> bytes:
    return _json_bytes(
        {
            "batch_id": commit.batch_id,
            "fingerprint": commit.fingerprint,
            "accepted_count": commit.accepted_count,
            "quarantine_count": commit.quarantine_count,
        }
    )


def commit_from_bytes(data: bytes) -> CommittedBatch:
    payload = _load(data)
    if not isinstance(payload, dict):
        raise ValueError("Persisted commit has invalid shape")
    return CommittedBatch(
        batch_id=str(payload["batch_id"]),
        fingerprint=str(payload["fingerprint"]),
        accepted_count=int(payload["accepted_count"]),
        quarantine_count=int(payload["quarantine_count"]),
    )
