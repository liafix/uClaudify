"""Storage ports for the FinBridge PASS 3 processing boundary.

The domain package stays storage-framework free. These protocols describe only the four persisted
surfaces required by the candidate demo: raw input, verified output, quarantine and audit/ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from finbridge_domain.ledger import CommittedBatch
from finbridge_domain.models import Transaction, ValidationIssue


@dataclass(frozen=True, slots=True)
class AuditEvent:
    batch_id: str
    event_id: str
    event_type: str
    payload: Mapping[str, object]


class RawBatchStore(Protocol):
    def put(self, batch_id: str, rows: tuple[Transaction, ...]) -> None: ...

    def get(self, batch_id: str) -> tuple[Transaction, ...] | None: ...


class ProcessedBatchStore(Protocol):
    def put(self, batch_id: str, rows: tuple[Transaction, ...]) -> None: ...

    def get(self, batch_id: str) -> tuple[Transaction, ...] | None: ...


class QuarantineStore(Protocol):
    def put(
        self,
        batch_id: str,
        rows: tuple[Transaction, ...],
        issues: tuple[ValidationIssue, ...],
    ) -> None: ...

    def get(self, batch_id: str) -> tuple[tuple[Transaction, ...], tuple[ValidationIssue, ...]] | None: ...


class AuditStore(Protocol):
    def put_event(self, event: AuditEvent) -> None: ...

    def list_events(self, batch_id: str) -> tuple[AuditEvent, ...]: ...

    def put_commit(self, commit: CommittedBatch) -> None: ...

    def get_commit(self, batch_id: str) -> CommittedBatch | None: ...

    def count_commits(self) -> int: ...


@dataclass(frozen=True, slots=True)
class StorageBundle:
    raw: RawBatchStore
    processed: ProcessedBatchStore
    quarantine: QuarantineStore
    audit: AuditStore
