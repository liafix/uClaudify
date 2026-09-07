"""Four persisted PASS 3 storage surfaces implemented over a blob backend."""

from __future__ import annotations

from finbridge_domain.ledger import CommittedBatch
from finbridge_domain.models import Transaction, ValidationIssue

from .blob_backend import BlobBackend
from .ports import AuditEvent, AuditStore, ProcessedBatchStore, QuarantineStore, RawBatchStore, StorageBundle
from .serialization import (
    audit_event_from_bytes,
    audit_event_to_bytes,
    batch_from_bytes,
    batch_to_bytes,
    commit_from_bytes,
    commit_to_bytes,
    quarantine_from_bytes,
    quarantine_to_bytes,
)


class StorageConflictError(RuntimeError):
    """Raised when immutable persisted evidence would be changed under the same key."""


def _put_immutable(backend: BlobBackend, container: str, name: str, data: bytes) -> None:
    existing = backend.get(container, name)
    if existing is not None and existing != data:
        raise StorageConflictError(f"Immutable blob conflict at {container}/{name}")
    backend.put(container, name, data)


class BlobRawBatchStore(RawBatchStore):
    CONTAINER = "raw"

    def __init__(self, backend: BlobBackend) -> None:
        self._backend = backend

    def put(self, batch_id: str, rows: tuple[Transaction, ...]) -> None:
        _put_immutable(self._backend, self.CONTAINER, f"{batch_id}/batch.json", batch_to_bytes(batch_id, rows))

    def get(self, batch_id: str) -> tuple[Transaction, ...] | None:
        data = self._backend.get(self.CONTAINER, f"{batch_id}/batch.json")
        if data is None:
            return None
        persisted_id, rows = batch_from_bytes(data)
        if persisted_id != batch_id:
            raise StorageConflictError("Raw batch key/payload id mismatch")
        return rows


class BlobProcessedBatchStore(ProcessedBatchStore):
    CONTAINER = "processed"

    def __init__(self, backend: BlobBackend) -> None:
        self._backend = backend

    def put(self, batch_id: str, rows: tuple[Transaction, ...]) -> None:
        _put_immutable(
            self._backend,
            self.CONTAINER,
            f"{batch_id}/accepted.json",
            batch_to_bytes(batch_id, rows),
        )

    def get(self, batch_id: str) -> tuple[Transaction, ...] | None:
        data = self._backend.get(self.CONTAINER, f"{batch_id}/accepted.json")
        if data is None:
            return None
        persisted_id, rows = batch_from_bytes(data)
        if persisted_id != batch_id:
            raise StorageConflictError("Processed batch key/payload id mismatch")
        return rows


class BlobQuarantineStore(QuarantineStore):
    CONTAINER = "quarantine"

    def __init__(self, backend: BlobBackend) -> None:
        self._backend = backend

    def put(
        self,
        batch_id: str,
        rows: tuple[Transaction, ...],
        issues: tuple[ValidationIssue, ...],
    ) -> None:
        _put_immutable(
            self._backend,
            self.CONTAINER,
            f"{batch_id}/quarantined.json",
            quarantine_to_bytes(batch_id, rows, issues),
        )

    def get(self, batch_id: str) -> tuple[tuple[Transaction, ...], tuple[ValidationIssue, ...]] | None:
        data = self._backend.get(self.CONTAINER, f"{batch_id}/quarantined.json")
        if data is None:
            return None
        persisted_id, rows, issues = quarantine_from_bytes(data)
        if persisted_id != batch_id:
            raise StorageConflictError("Quarantine key/payload id mismatch")
        return rows, issues


class BlobAuditStore(AuditStore):
    CONTAINER = "audit"

    def __init__(self, backend: BlobBackend) -> None:
        self._backend = backend

    def put_event(self, event: AuditEvent) -> None:
        data = audit_event_to_bytes(
            batch_id=event.batch_id,
            event_id=event.event_id,
            event_type=event.event_type,
            payload=event.payload,
        )
        _put_immutable(
            self._backend,
            self.CONTAINER,
            f"{event.batch_id}/events/{event.event_id}.json",
            data,
        )

    def list_events(self, batch_id: str) -> tuple[AuditEvent, ...]:
        events: list[AuditEvent] = []
        for name in self._backend.list_names(self.CONTAINER, f"{batch_id}/events/"):
            data = self._backend.get(self.CONTAINER, name)
            if data is None:
                raise StorageConflictError(f"Audit event disappeared while listing: {name}")
            persisted_batch, event_id, event_type, payload = audit_event_from_bytes(data)
            if persisted_batch != batch_id:
                raise StorageConflictError("Audit event key/payload batch mismatch")
            events.append(AuditEvent(batch_id, event_id, event_type, payload))
        return tuple(sorted(events, key=lambda event: event.event_id))

    def put_commit(self, commit: CommittedBatch) -> None:
        _put_immutable(
            self._backend,
            self.CONTAINER,
            f"{commit.batch_id}/commit.json",
            commit_to_bytes(commit),
        )

    def get_commit(self, batch_id: str) -> CommittedBatch | None:
        data = self._backend.get(self.CONTAINER, f"{batch_id}/commit.json")
        if data is None:
            return None
        commit = commit_from_bytes(data)
        if commit.batch_id != batch_id:
            raise StorageConflictError("Commit key/payload id mismatch")
        return commit

    def count_commits(self) -> int:
        return len(tuple(name for name in self._backend.list_names(self.CONTAINER) if name.endswith("/commit.json")))


def build_blob_storage(backend: BlobBackend) -> StorageBundle:
    return StorageBundle(
        raw=BlobRawBatchStore(backend),
        processed=BlobProcessedBatchStore(backend),
        quarantine=BlobQuarantineStore(backend),
        audit=BlobAuditStore(backend),
    )
