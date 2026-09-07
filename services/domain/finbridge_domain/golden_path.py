"""Utilities for executing and serializing the PASS 1 candidate-demo golden path."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from .fixtures import build_synthetic_legacy_batch
from .models import PipelineSnapshot
from .pipeline import GoldenPathPipeline


def _decimal(value: Decimal) -> str:
    return f"{value:.2f}"


def snapshot_to_dict(snapshot: PipelineSnapshot) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "state": snapshot.state.value,
        "input_records": snapshot.input_records,
        "accepted_records": snapshot.accepted_records,
        "anomaly_records": snapshot.anomaly_records,
        "quarantined_records": snapshot.quarantined_records,
        "unaccounted_records": snapshot.unaccounted_records,
        "issues": [
            {
                "transaction_id": issue.transaction_id,
                "source_line": issue.source_line,
                "rule": issue.rule,
                "reason": issue.reason,
            }
            for issue in snapshot.issues
        ],
    }
    if snapshot.reconciliation is not None:
        payload["reconciliation"] = {
            "opening_balance_eur": _decimal(snapshot.reconciliation.opening_balance_eur),
            "credits_eur": _decimal(snapshot.reconciliation.credits_eur),
            "debits_eur": _decimal(snapshot.reconciliation.debits_eur),
            "expected_closing_balance_eur": _decimal(
                snapshot.reconciliation.expected_closing_balance_eur
            ),
            "calculated_closing_balance_eur": _decimal(
                snapshot.reconciliation.calculated_closing_balance_eur
            ),
            "difference_eur": _decimal(snapshot.reconciliation.difference_eur),
            "reconciled": snapshot.reconciliation.reconciled,
        }
    if snapshot.replay is not None:
        payload["replay"] = {
            "batch_id": snapshot.replay.batch_id,
            "previously_processed": snapshot.replay.previously_processed,
            "new_accepted_records": snapshot.replay.new_accepted_records,
            "duplicate_imports": snapshot.replay.duplicate_imports,
            "additional_quarantine_rows": snapshot.replay.additional_quarantine_rows,
        }
    return payload


def run_golden_path() -> dict[str, Any]:
    pipeline = GoldenPathPipeline(build_synthetic_legacy_batch())
    received = snapshot_to_dict(pipeline.snapshot())
    blocked = snapshot_to_dict(pipeline.process_to_quality_gate())
    quarantined = snapshot_to_dict(pipeline.quarantine_invalid_records())
    reconciled = snapshot_to_dict(pipeline.reconcile())
    replayed = snapshot_to_dict(pipeline.replay_batch())
    ready = snapshot_to_dict(pipeline.confirm_analytics_readiness())

    return {
        "batch_id": "2026-09-05-001",
        "source_system": "AlpineBank Legacy Finance",
        "synthetic": True,
        "stages": [received, blocked, quarantined, reconciled, replayed, ready],
        "state_history": [state.value for state in pipeline.history],
    }
