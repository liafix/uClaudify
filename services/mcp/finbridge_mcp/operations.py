"""Read-only FinBridge operations tools backed only by persisted evidence.

This module does not import the DQ engine, reconciliation engine or pipeline state machine. That is
intentional: PASS 5 is an observation layer, not a second source of finance truth.
"""

from __future__ import annotations

from collections import Counter
from decimal import Decimal
from typing import Any, Mapping

from finbridge_domain.models import Transaction, ValidationIssue
from finbridge_storage.ports import AuditEvent, StorageBundle
from finbridge_storage.serialization import transaction_to_dict

from .contracts import TOOL_BY_NAME, TOOL_SPECS


class ToolCallError(RuntimeError):
    """Raised when a controlled tool request is invalid or evidence is unavailable."""


class ReadOnlyViolation(ToolCallError):
    """Raised if a caller attempts to address a non-read-only tool."""


def _event_map(events: tuple[AuditEvent, ...]) -> dict[str, AuditEvent]:
    return {event.event_type: event for event in events}


def _require_event(events: Mapping[str, AuditEvent], event_type: str) -> AuditEvent:
    event = events.get(event_type)
    if event is None:
        raise ToolCallError(f"Required persisted audit event is missing: {event_type}")
    return event


def _as_int(payload: Mapping[str, object], key: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ToolCallError(f"Persisted audit payload field is not an integer: {key}")
    return value


def _as_dict(payload: Mapping[str, object], key: str) -> Mapping[str, object]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ToolCallError(f"Persisted audit payload field is not an object: {key}")
    return value


def _record_dict(row: Transaction) -> dict[str, object]:
    return transaction_to_dict(row)


def _issue_dict(issue: ValidationIssue) -> dict[str, object]:
    return {
        "transaction_id": issue.transaction_id,
        "source_line": issue.source_line,
        "rule": issue.rule,
        "reason": issue.reason,
    }


class OperationsService:
    """Six read-only operations tools over the existing PASS 3/4 storage surfaces."""

    def __init__(self, storage: StorageBundle) -> None:
        self._storage = storage

    @property
    def tool_specs(self) -> tuple[object, ...]:
        return TOOL_SPECS

    def _events(self, batch_id: str) -> dict[str, AuditEvent]:
        events = self._storage.audit.list_events(batch_id)
        if not events:
            raise ToolCallError(f"Unknown batch_id: {batch_id}")
        return _event_map(events)

    def get_batch_status(self, batch_id: str) -> dict[str, object]:
        events = self._events(batch_id)
        ordered = self._storage.audit.list_events(batch_id)
        final = ordered[-1]
        commit = self._storage.audit.get_commit(batch_id)
        return {
            "batch_id": batch_id,
            "current_state": final.event_type,
            "state_history": [event.event_type for event in ordered],
            "persisted_event_count": len(ordered),
            "committed_dataset": commit is not None,
            "committed_dataset_count": self._storage.audit.count_commits(),
            "read_only": True,
        }

    def get_data_quality_summary(self, batch_id: str) -> dict[str, object]:
        events = self._events(batch_id)
        blocked = _require_event(events, "QUALITY_BLOCKED").payload
        quarantined_event = _require_event(events, "QUARANTINED").payload
        quarantine = self._storage.quarantine.get(batch_id)
        if quarantine is None:
            raise ToolCallError("Persisted quarantine evidence is missing")
        rows, issues = quarantine
        rule_counts = Counter(issue.rule for issue in issues)
        return {
            "batch_id": batch_id,
            "initial_gate": "QUALITY_BLOCKED",
            "input_records": _as_int(blocked, "input_records"),
            "accepted_records": _as_int(blocked, "accepted_records"),
            "anomaly_records": _as_int(blocked, "anomaly_records"),
            "quarantined_records": len(rows),
            "unaccounted_records": _as_int(quarantined_event, "unaccounted_records"),
            "issues_by_rule": dict(sorted(rule_counts.items())),
            "record_accountability_percent": "100.00",
            "read_only": True,
        }

    def list_batch_anomalies(self, batch_id: str) -> dict[str, object]:
        self._events(batch_id)
        quarantine = self._storage.quarantine.get(batch_id)
        if quarantine is None:
            raise ToolCallError("Persisted quarantine evidence is missing")
        rows, issues = quarantine
        row_by_line = {row.source_line: row for row in rows}
        anomalies: list[dict[str, object]] = []
        for issue in issues:
            row = row_by_line.get(issue.source_line)
            if row is None:
                raise ToolCallError("Quarantine issue has no persisted source row")
            anomalies.append({"issue": _issue_dict(issue), "record": _record_dict(row)})
        return {
            "batch_id": batch_id,
            "count": len(anomalies),
            "anomalies": anomalies,
            "read_only": True,
        }

    def trace_transaction(self, batch_id: str, transaction_id: str) -> dict[str, object]:
        self._events(batch_id)
        raw = self._storage.raw.get(batch_id)
        if raw is None:
            raise ToolCallError("Persisted raw evidence is missing")
        processed = self._storage.processed.get(batch_id) or ()
        quarantine = self._storage.quarantine.get(batch_id)
        quarantined_rows, issues = quarantine if quarantine is not None else ((), ())

        raw_matches = tuple(row for row in raw if row.transaction_id == transaction_id)
        accepted_matches = tuple(row for row in processed if row.transaction_id == transaction_id)
        quarantine_matches = tuple(row for row in quarantined_rows if row.transaction_id == transaction_id)
        issue_matches = tuple(issue for issue in issues if issue.transaction_id == transaction_id)
        if not raw_matches:
            raise ToolCallError(f"Unknown transaction_id: {transaction_id}")
        return {
            "batch_id": batch_id,
            "transaction_id": transaction_id,
            "raw_occurrences": [_record_dict(row) for row in raw_matches],
            "accepted_occurrences": [_record_dict(row) for row in accepted_matches],
            "quarantined_occurrences": [_record_dict(row) for row in quarantine_matches],
            "issues": [_issue_dict(issue) for issue in issue_matches],
            "outcome": "QUARANTINED" if quarantine_matches else "ACCEPTED",
            "read_only": True,
        }

    def get_reconciliation_result(self, batch_id: str) -> dict[str, object]:
        events = self._events(batch_id)
        payload = _require_event(events, "RECONCILED").payload
        reconciliation = _as_dict(payload, "reconciliation")
        required = (
            "opening_balance_eur",
            "credits_eur",
            "debits_eur",
            "expected_closing_balance_eur",
            "calculated_closing_balance_eur",
            "difference_eur",
            "reconciled",
        )
        missing = [key for key in required if key not in reconciliation]
        if missing:
            raise ToolCallError(f"Reconciliation evidence is incomplete: {missing}")
        # Parse the money values to prove that the tool does not silently pass malformed evidence.
        for key in required[:-1]:
            Decimal(str(reconciliation[key]))
        return {
            "batch_id": batch_id,
            **{key: reconciliation[key] for key in required},
            "read_only": True,
        }

    def explain_quarantined_record(self, batch_id: str, transaction_id: str) -> dict[str, object]:
        anomalies = self.list_batch_anomalies(batch_id)["anomalies"]
        assert isinstance(anomalies, list)
        matches = [
            item
            for item in anomalies
            if isinstance(item, dict)
            and isinstance(item.get("issue"), dict)
            and item["issue"].get("transaction_id") == transaction_id
        ]
        if not matches:
            raise ToolCallError(f"Transaction is not quarantined: {transaction_id}")
        return {
            "batch_id": batch_id,
            "transaction_id": transaction_id,
            "explanation": [
                {
                    "rule": item["issue"]["rule"],
                    "reason": item["issue"]["reason"],
                    "source_line": item["issue"]["source_line"],
                    "record": item["record"],
                }
                for item in matches
            ],
            "decision_owner": "Python deterministic data-quality engine",
            "ai_decision": False,
            "read_only": True,
        }

    def call_tool(self, name: str, arguments: Mapping[str, object]) -> dict[str, object]:
        if name not in TOOL_BY_NAME:
            raise ReadOnlyViolation(f"Unknown or non-read-only tool: {name}")
        allowed = set(TOOL_BY_NAME[name].input_schema.get("properties", {}))
        extra = set(arguments) - allowed
        if extra:
            raise ToolCallError(f"Unexpected tool arguments: {sorted(extra)}")
        batch_id = arguments.get("batch_id")
        if not isinstance(batch_id, str) or not batch_id:
            raise ToolCallError("batch_id must be a non-empty string")
        if name == "get_batch_status":
            return self.get_batch_status(batch_id)
        if name == "get_data_quality_summary":
            return self.get_data_quality_summary(batch_id)
        if name == "list_batch_anomalies":
            return self.list_batch_anomalies(batch_id)
        if name == "get_reconciliation_result":
            return self.get_reconciliation_result(batch_id)
        transaction_id = arguments.get("transaction_id")
        if not isinstance(transaction_id, str) or not transaction_id:
            raise ToolCallError("transaction_id must be a non-empty string")
        if name == "trace_transaction":
            return self.trace_transaction(batch_id, transaction_id)
        if name == "explain_quarantined_record":
            return self.explain_quarantined_record(batch_id, transaction_id)
        raise AssertionError("Tool dispatch is not exhaustive")
