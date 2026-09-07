from __future__ import annotations

import unittest

from finbridge_domain.contracts import FROZEN_SCENARIO
from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_domain.ledger import CommittedBatch, fingerprint_batch
from finbridge_domain.models import ValidationIssue
from finbridge_storage import AuditEvent, StorageConflictError, build_in_memory_storage


class StorageContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = build_in_memory_storage()
        self.batch = build_synthetic_legacy_batch()

    def test_raw_processed_quarantine_audit_round_trip(self) -> None:
        batch_id = FROZEN_SCENARIO.batch_id
        accepted = self.batch[:10]
        quarantined = self.batch[-2:]
        issues = (
            ValidationIssue("TX-X", 100, "DQ-02", "INVALID_CURRENCY:EUX"),
            ValidationIssue("TX-Y", 101, "DQ-01", "DUPLICATE_TRANSACTION"),
        )

        self.storage.raw.put(batch_id, self.batch)
        self.storage.processed.put(batch_id, accepted)
        self.storage.quarantine.put(batch_id, quarantined, issues)
        self.storage.audit.put_event(
            AuditEvent(batch_id, "001", "TEST", {"count": 2, "status": "PASS"})
        )
        commit = CommittedBatch(batch_id, fingerprint_batch(self.batch), 10, 2)
        self.storage.audit.put_commit(commit)

        self.assertEqual(self.storage.raw.get(batch_id), self.batch)
        self.assertEqual(self.storage.processed.get(batch_id), accepted)
        self.assertEqual(self.storage.quarantine.get(batch_id), (quarantined, issues))
        self.assertEqual(self.storage.audit.list_events(batch_id)[0].event_type, "TEST")
        self.assertEqual(self.storage.audit.get_commit(batch_id), commit)
        self.assertEqual(self.storage.audit.count_commits(), 1)

    def test_immutable_raw_evidence_rejects_changed_content(self) -> None:
        batch_id = FROZEN_SCENARIO.batch_id
        self.storage.raw.put(batch_id, self.batch)
        changed = list(self.batch)
        changed[-1] = changed[-1].__class__(
            transaction_id=changed[-1].transaction_id,
            account_id=changed[-1].account_id,
            booking_date=changed[-1].booking_date,
            amount=changed[-1].amount,
            currency="USD",
            direction=changed[-1].direction,
            counterparty=changed[-1].counterparty,
            source_system=changed[-1].source_system,
            source_line=changed[-1].source_line,
        )
        with self.assertRaises(StorageConflictError):
            self.storage.raw.put(batch_id, tuple(changed))


if __name__ == "__main__":
    unittest.main()
