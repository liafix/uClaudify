from __future__ import annotations

import unittest

from batch_processor.handler import process_raw_blob
from finbridge_domain.contracts import FROZEN_SCENARIO
from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_domain.golden_path import run_golden_path
from finbridge_storage import build_in_memory_storage
from finbridge_storage.serialization import batch_to_bytes


class AzureFunctionBoundaryTests(unittest.TestCase):
    def test_blob_trigger_handler_only_orchestrates_existing_raw_evidence(self) -> None:
        storage = build_in_memory_storage()
        batch = build_synthetic_legacy_batch()
        storage.raw.put(FROZEN_SCENARIO.batch_id, batch)
        result = process_raw_blob(batch_to_bytes(FROZEN_SCENARIO.batch_id, batch), storage)

        self.assertEqual(result, run_golden_path())
        self.assertEqual(len(storage.processed.get(FROZEN_SCENARIO.batch_id) or ()), 1019)
        self.assertEqual(storage.audit.count_commits(), 1)

    def test_trigger_rejects_payload_that_does_not_match_persisted_raw_blob(self) -> None:
        storage = build_in_memory_storage()
        batch = build_synthetic_legacy_batch()
        storage.raw.put(FROZEN_SCENARIO.batch_id, batch)
        changed = list(batch)
        row = changed[-1]
        changed[-1] = row.__class__(
            transaction_id=row.transaction_id,
            account_id=row.account_id,
            booking_date=row.booking_date,
            amount=row.amount,
            currency="USD",
            direction=row.direction,
            counterparty=row.counterparty,
            source_system=row.source_system,
            source_line=row.source_line,
        )
        with self.assertRaises(RuntimeError):
            process_raw_blob(batch_to_bytes(FROZEN_SCENARIO.batch_id, tuple(changed)), storage)


if __name__ == "__main__":
    unittest.main()
