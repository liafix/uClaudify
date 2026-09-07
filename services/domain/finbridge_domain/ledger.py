"""Deterministic in-memory import ledger for DQ-05 and FIN-05.

PASS 2 deliberately uses an in-memory ledger; a storage-backed implementation belongs to PASS 3.
The important contract is already executable: a batch id is immutable once committed and exact
replay must never create a second import/dataset.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable, Protocol

from .models import ReplayResult, Transaction


class BatchConflictError(RuntimeError):
    """Raised when a known batch id is replayed with changed content."""


@dataclass(frozen=True, slots=True)
class CommittedBatch:
    batch_id: str
    fingerprint: str
    accepted_count: int
    quarantine_count: int


def fingerprint_batch(rows: Iterable[Transaction]) -> str:
    digest = sha256()
    for row in sorted(tuple(rows), key=lambda item: item.source_line):
        digest.update(
            "\x1f".join(
                (
                    str(row.source_line),
                    row.transaction_id,
                    row.account_id,
                    row.booking_date,
                    format(row.amount, "f"),
                    row.currency,
                    row.direction,
                    row.counterparty,
                    row.source_system,
                )
            ).encode("utf-8")
        )
        digest.update(b"\n")
    return digest.hexdigest()




class BatchLedger(Protocol):
    @property
    def dataset_count(self) -> int: ...

    def commit(
        self,
        batch_id: str,
        batch: Iterable[Transaction],
        *,
        accepted_count: int,
        quarantine_count: int,
    ) -> None: ...

    def replay(self, batch_id: str, batch: Iterable[Transaction]) -> ReplayResult: ...

class InMemoryBatchLedger:
    def __init__(self) -> None:
        self._datasets: dict[str, CommittedBatch] = {}

    @property
    def dataset_count(self) -> int:
        return len(self._datasets)

    def commit(
        self,
        batch_id: str,
        batch: Iterable[Transaction],
        *,
        accepted_count: int,
        quarantine_count: int,
    ) -> None:
        rows = tuple(batch)
        fingerprint = fingerprint_batch(rows)
        existing = self._datasets.get(batch_id)
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
                    f"Batch id {batch_id} was replayed with different decision counts"
                )
            return
        self._datasets[batch_id] = CommittedBatch(
            batch_id=batch_id,
            fingerprint=fingerprint,
            accepted_count=accepted_count,
            quarantine_count=quarantine_count,
        )

    def replay(self, batch_id: str, batch: Iterable[Transaction]) -> ReplayResult:
        rows = tuple(batch)
        existing = self._datasets.get(batch_id)
        if existing is None:
            raise BatchConflictError(f"Batch id {batch_id} has not been committed")
        if existing.fingerprint != fingerprint_batch(rows):
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
