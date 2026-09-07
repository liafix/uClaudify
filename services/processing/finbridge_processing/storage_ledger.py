"""Storage-backed DQ-05 / FIN-05 ledger for PASS 3."""

from __future__ import annotations

from typing import Iterable

from finbridge_domain.ledger import BatchConflictError, CommittedBatch, fingerprint_batch
from finbridge_domain.models import ReplayResult, Transaction
from finbridge_storage.ports import AuditStore


class StorageBackedBatchLedger:
    def __init__(self, audit: AuditStore) -> None:
        self._audit = audit

    @property
    def dataset_count(self) -> int:
        return self._audit.count_commits()

    def commit(
        self,
        batch_id: str,
        batch: Iterable[Transaction],
        *,
        accepted_count: int,
        quarantine_count: int,
    ) -> None:
        fingerprint = fingerprint_batch(tuple(batch))
        existing = self._audit.get_commit(batch_id)
        if existing is not None:
            if existing.fingerprint != fingerprint:
                raise BatchConflictError(
                    f"Batch id {batch_id} was replayed with different source content"
                )
            if (
                existing.accepted_count != accepted_count
                or existing.quarantine_count != quarantine_count
            ):
                raise BatchConflictError(
                    f"Batch id {batch_id} was replayed with different persisted outcomes"
                )
            return
        self._audit.put_commit(
            CommittedBatch(
                batch_id=batch_id,
                fingerprint=fingerprint,
                accepted_count=accepted_count,
                quarantine_count=quarantine_count,
            )
        )

    def replay(self, batch_id: str, batch: Iterable[Transaction]) -> ReplayResult:
        existing = self._audit.get_commit(batch_id)
        if existing is None:
            raise BatchConflictError(f"Batch id {batch_id} has not been committed")
        if existing.fingerprint != fingerprint_batch(tuple(batch)):
            raise BatchConflictError(
                f"Batch id {batch_id} was replayed with different source content"
            )
        return ReplayResult(
            batch_id=batch_id,
            previously_processed=True,
            new_accepted_records=0,
            duplicate_imports=0,
            additional_quarantine_rows=0,
        )
