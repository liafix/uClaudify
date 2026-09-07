from __future__ import annotations

import unittest

from finbridge_domain.contracts import FROZEN_SCENARIO
from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_mcp import OperationsService
from finbridge_processing import ProcessingOrchestrator
from finbridge_storage import build_in_memory_storage


class ReadOnlyBoundaryTests(unittest.TestCase):
    def test_all_tools_leave_persisted_evidence_byte_semantics_unchanged(self) -> None:
        storage = build_in_memory_storage()
        ProcessingOrchestrator(storage).run_golden_path(build_synthetic_legacy_batch())
        batch_id = FROZEN_SCENARIO.batch_id
        before = (
            storage.raw.get(batch_id),
            storage.processed.get(batch_id),
            storage.quarantine.get(batch_id),
            storage.audit.list_events(batch_id),
            storage.audit.get_commit(batch_id),
            storage.audit.count_commits(),
        )
        ops = OperationsService(storage)
        ops.get_batch_status(batch_id)
        ops.get_data_quality_summary(batch_id)
        ops.list_batch_anomalies(batch_id)
        ops.trace_transaction(batch_id, "TX-00482")
        ops.get_reconciliation_result(batch_id)
        ops.explain_quarantined_record(batch_id, "TX-01011")
        after = (
            storage.raw.get(batch_id),
            storage.processed.get(batch_id),
            storage.quarantine.get(batch_id),
            storage.audit.list_events(batch_id),
            storage.audit.get_commit(batch_id),
            storage.audit.count_commits(),
        )
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
