"""PASS 3 orchestration boundary: domain decisions + persisted evidence.

The orchestrator owns storage sequencing only. All DQ and finance decisions remain in
`finbridge_domain.GoldenPathPipeline`, keeping Azure Functions as a thin trigger adapter.
"""

from __future__ import annotations

from typing import Any

from finbridge_domain.contracts import FROZEN_SCENARIO
from finbridge_domain.golden_path import snapshot_to_dict
from finbridge_domain.models import PipelineSnapshot, Transaction
from finbridge_domain.pipeline import GoldenPathPipeline
from finbridge_storage.ports import AuditEvent, StorageBundle

from .storage_ledger import StorageBackedBatchLedger


class ProcessingOrchestrator:
    def __init__(self, storage: StorageBundle) -> None:
        self._storage = storage

    def _event(self, event_id: str, event_type: str, snapshot: PipelineSnapshot) -> None:
        evidence = snapshot_to_dict(snapshot)
        self._storage.audit.put_event(
            AuditEvent(
                batch_id=FROZEN_SCENARIO.batch_id,
                event_id=event_id,
                event_type=event_type,
                payload={key: value for key, value in evidence.items() if key != "issues"},
            )
        )

    def run_golden_path(
        self,
        batch: tuple[Transaction, ...],
        *,
        raw_already_persisted: bool = False,
    ) -> dict[str, Any]:
        batch_id = FROZEN_SCENARIO.batch_id
        if not raw_already_persisted:
            self._storage.raw.put(batch_id, batch)
        else:
            persisted = self._storage.raw.get(batch_id)
            if persisted is None:
                raise RuntimeError("Azure trigger boundary requires the raw blob to exist")
            if persisted != batch:
                raise RuntimeError("Triggered raw blob does not match persisted raw evidence")

        ledger = StorageBackedBatchLedger(self._storage.audit)
        pipeline = GoldenPathPipeline(batch, ledger=ledger)
        received = pipeline.snapshot()
        self._event("000-received", "RECEIVED", received)

        blocked = pipeline.process_to_quality_gate()
        self._event("010-quality-blocked", "QUALITY_BLOCKED", blocked)

        quarantined = pipeline.quarantine_invalid_records()
        self._storage.quarantine.put(batch_id, pipeline.quarantined, pipeline.issues)
        self._event("020-quarantined", "QUARANTINED", quarantined)

        reconciled = pipeline.reconcile()
        self._storage.processed.put(batch_id, pipeline.accepted)
        self._event("030-reconciled", "RECONCILED", reconciled)

        replayed = pipeline.replay_batch()
        self._event("040-idempotency-pass", "IDEMPOTENCY_PASS", replayed)

        ready = pipeline.confirm_analytics_readiness()
        self._event("050-ready-for-analytics", "READY_FOR_ANALYTICS", ready)

        return {
            "batch_id": batch_id,
            "source_system": FROZEN_SCENARIO.source_system,
            "synthetic": True,
            "stages": [
                snapshot_to_dict(received),
                snapshot_to_dict(blocked),
                snapshot_to_dict(quarantined),
                snapshot_to_dict(reconciled),
                snapshot_to_dict(replayed),
                snapshot_to_dict(ready),
            ],
            "state_history": [state.value for state in pipeline.history],
        }
