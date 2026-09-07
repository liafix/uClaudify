from __future__ import annotations

import unittest

from finbridge_domain.contracts import FROZEN_SCENARIO
from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_domain.golden_path import run_golden_path
from finbridge_processing import ProcessingOrchestrator
from finbridge_storage import build_in_memory_storage


class Pass3ProcessingBoundaryTests(unittest.TestCase):
    def test_storage_backed_golden_path_is_evidence_identical(self) -> None:
        storage = build_in_memory_storage()
        runtime = ProcessingOrchestrator(storage).run_golden_path(build_synthetic_legacy_batch())

        self.assertEqual(runtime, run_golden_path())
        self.assertEqual(len(storage.raw.get(FROZEN_SCENARIO.batch_id) or ()), 1024)
        self.assertEqual(len(storage.processed.get(FROZEN_SCENARIO.batch_id) or ()), 1019)
        quarantined = storage.quarantine.get(FROZEN_SCENARIO.batch_id)
        self.assertIsNotNone(quarantined)
        assert quarantined is not None
        self.assertEqual(len(quarantined[0]), 5)
        self.assertEqual(len(quarantined[1]), 5)
        self.assertEqual(storage.audit.count_commits(), 1)
        self.assertEqual(
            [event.event_type for event in storage.audit.list_events(FROZEN_SCENARIO.batch_id)],
            [
                "RECEIVED",
                "QUALITY_BLOCKED",
                "QUARANTINED",
                "RECONCILED",
                "IDEMPOTENCY_PASS",
                "READY_FOR_ANALYTICS",
            ],
        )

    def test_fresh_orchestrator_replay_keeps_one_persisted_dataset(self) -> None:
        storage = build_in_memory_storage()
        batch = build_synthetic_legacy_batch()
        first = ProcessingOrchestrator(storage).run_golden_path(batch)
        second = ProcessingOrchestrator(storage).run_golden_path(batch)

        self.assertEqual(first, second)
        self.assertEqual(storage.audit.count_commits(), 1)
        self.assertEqual(len(storage.audit.list_events(FROZEN_SCENARIO.batch_id)), 6)
        self.assertEqual(len(storage.processed.get(FROZEN_SCENARIO.batch_id) or ()), 1019)


if __name__ == "__main__":
    unittest.main()
