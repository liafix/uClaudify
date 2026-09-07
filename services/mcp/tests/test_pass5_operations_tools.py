from __future__ import annotations

import unittest

from finbridge_domain.contracts import FROZEN_SCENARIO
from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_mcp import OperationsService, ReadOnlyViolation
from finbridge_processing import ProcessingOrchestrator
from finbridge_storage import build_in_memory_storage


class Pass5OperationsToolsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.storage = build_in_memory_storage()
        ProcessingOrchestrator(self.storage).run_golden_path(build_synthetic_legacy_batch())
        self.ops = OperationsService(self.storage)
        self.batch_id = FROZEN_SCENARIO.batch_id

    def test_batch_status_is_ready_and_read_only(self) -> None:
        result = self.ops.get_batch_status(self.batch_id)
        self.assertEqual(result["current_state"], "READY_FOR_ANALYTICS")
        self.assertEqual(result["committed_dataset_count"], 1)
        self.assertIs(result["read_only"], True)

    def test_quality_summary_preserves_frozen_counts(self) -> None:
        result = self.ops.get_data_quality_summary(self.batch_id)
        self.assertEqual(result["input_records"], 1024)
        self.assertEqual(result["accepted_records"], 1019)
        self.assertEqual(result["anomaly_records"], 5)
        self.assertEqual(result["quarantined_records"], 5)
        self.assertEqual(result["unaccounted_records"], 0)
        self.assertEqual(result["issues_by_rule"], {"DQ-01": 3, "DQ-02": 2})

    def test_anomalies_include_exact_five_records(self) -> None:
        result = self.ops.list_batch_anomalies(self.batch_id)
        self.assertEqual(result["count"], 5)
        anomalies = result["anomalies"]
        self.assertEqual(
            [item["issue"]["transaction_id"] for item in anomalies],
            ["TX-00482", "TX-00791", "TX-00902", "TX-01011", "TX-01012"],
        )

    def test_trace_duplicate_shows_raw_and_quarantine_occurrences(self) -> None:
        result = self.ops.trace_transaction(self.batch_id, "TX-00482")
        self.assertEqual(result["outcome"], "QUARANTINED")
        self.assertEqual(len(result["raw_occurrences"]), 2)
        self.assertEqual(len(result["accepted_occurrences"]), 1)
        self.assertEqual(len(result["quarantined_occurrences"]), 1)
        self.assertEqual(result["issues"][0]["rule"], "DQ-01")

    def test_reconciliation_reads_exact_zero_difference(self) -> None:
        result = self.ops.get_reconciliation_result(self.batch_id)
        self.assertEqual(result["expected_closing_balance_eur"], "1026700.00")
        self.assertEqual(result["calculated_closing_balance_eur"], "1026700.00")
        self.assertEqual(result["difference_eur"], "0.00")
        self.assertIs(result["reconciled"], True)

    def test_explain_quarantined_record_reports_python_owner(self) -> None:
        result = self.ops.explain_quarantined_record(self.batch_id, "TX-01011")
        self.assertEqual(result["explanation"][0]["rule"], "DQ-02")
        self.assertEqual(result["explanation"][0]["reason"], "INVALID_CURRENCY:EUX")
        self.assertEqual(result["decision_owner"], "Python deterministic data-quality engine")
        self.assertIs(result["ai_decision"], False)

    def test_unknown_tool_fails_closed(self) -> None:
        with self.assertRaises(ReadOnlyViolation):
            self.ops.call_tool("delete_batch", {"batch_id": self.batch_id})


if __name__ == "__main__":
    unittest.main()
