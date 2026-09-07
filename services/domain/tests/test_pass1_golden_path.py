from decimal import Decimal
import unittest

from finbridge_domain.contracts import FROZEN_SCENARIO, GoldenState
from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_domain.golden_path import run_golden_path
from finbridge_domain.pipeline import GoldenPathPipeline, InvalidTransitionError


class Pass1GoldenPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.batch = build_synthetic_legacy_batch()
        self.pipeline = GoldenPathPipeline(self.batch)

    def test_fixture_has_exact_frozen_shape(self) -> None:
        self.assertEqual(len(self.batch), 1024)
        self.assertEqual(len({row.source_line for row in self.batch}), 1024)
        self.assertTrue(all(row.source_system == FROZEN_SCENARIO.source_system for row in self.batch))

    def test_quality_gate_blocks_with_exact_five_anomalies(self) -> None:
        snapshot = self.pipeline.process_to_quality_gate()
        self.assertEqual(snapshot.state, GoldenState.QUALITY_BLOCKED)
        self.assertEqual(snapshot.accepted_records, 1019)
        self.assertEqual(snapshot.anomaly_records, 5)
        self.assertEqual(snapshot.quarantined_records, 0)
        self.assertEqual(snapshot.unaccounted_records, 0)
        self.assertEqual(
            [(issue.transaction_id, issue.rule, issue.reason) for issue in snapshot.issues],
            [
                ("TX-00482", "DQ-01", "DUPLICATE_TRANSACTION"),
                ("TX-00791", "DQ-01", "DUPLICATE_TRANSACTION"),
                ("TX-00902", "DQ-01", "DUPLICATE_TRANSACTION"),
                ("TX-01011", "DQ-02", "INVALID_CURRENCY:EUX"),
                ("TX-01012", "DQ-02", "INVALID_CURRENCY:EURO"),
            ],
        )

    def test_quarantine_produces_exact_record_accountability(self) -> None:
        self.pipeline.process_to_quality_gate()
        snapshot = self.pipeline.quarantine_invalid_records()
        self.assertEqual(snapshot.state, GoldenState.QUARANTINED)
        self.assertEqual(snapshot.accepted_records, 1019)
        self.assertEqual(snapshot.quarantined_records, 5)
        self.assertEqual(snapshot.unaccounted_records, 0)
        self.assertEqual(snapshot.accepted_records + snapshot.quarantined_records, 1024)

    def test_reconciliation_is_exact_decimal_and_zero_difference(self) -> None:
        self.pipeline.process_to_quality_gate()
        self.pipeline.quarantine_invalid_records()
        snapshot = self.pipeline.reconcile()
        result = snapshot.reconciliation
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.credits_eur, Decimal("125400.00"))
        self.assertEqual(result.debits_eur, Decimal("98700.00"))
        self.assertEqual(result.calculated_closing_balance_eur, Decimal("1026700.00"))
        self.assertEqual(result.difference_eur, Decimal("0.00"))
        self.assertTrue(result.reconciled)

    def test_replay_is_idempotent(self) -> None:
        self.pipeline.process_to_quality_gate()
        self.pipeline.quarantine_invalid_records()
        self.pipeline.reconcile()
        snapshot = self.pipeline.replay_batch()
        replay = snapshot.replay
        self.assertIsNotNone(replay)
        assert replay is not None
        self.assertTrue(replay.previously_processed)
        self.assertEqual(replay.new_accepted_records, 0)
        self.assertEqual(replay.duplicate_imports, 0)
        self.assertEqual(replay.additional_quarantine_rows, 0)

    def test_final_state_is_ready_for_analytics(self) -> None:
        self.pipeline.process_to_quality_gate()
        self.pipeline.quarantine_invalid_records()
        self.pipeline.reconcile()
        self.pipeline.replay_batch()
        snapshot = self.pipeline.confirm_analytics_readiness()
        self.assertEqual(snapshot.state, GoldenState.READY_FOR_ANALYTICS)
        self.assertEqual(snapshot.unaccounted_records, 0)
        self.assertEqual(
            list(self.pipeline.history),
            [
                GoldenState.RECEIVED,
                GoldenState.INGESTION_PASS,
                GoldenState.SCHEMA_PASS,
                GoldenState.NORMALIZATION_PASS,
                GoldenState.QUALITY_BLOCKED,
                GoldenState.QUARANTINED,
                GoldenState.RECONCILED,
                GoldenState.IDEMPOTENCY_PASS,
                GoldenState.READY_FOR_ANALYTICS,
            ],
        )

    def test_state_machine_is_fail_closed(self) -> None:
        with self.assertRaises(InvalidTransitionError):
            self.pipeline.reconcile()
        with self.assertRaises(InvalidTransitionError):
            self.pipeline.replay_batch()
        with self.assertRaises(InvalidTransitionError):
            self.pipeline.confirm_analytics_readiness()

    def test_golden_path_export_is_deterministic(self) -> None:
        first = run_golden_path()
        second = run_golden_path()
        self.assertEqual(first, second)
        self.assertEqual(first["stages"][-1]["state"], "READY_FOR_ANALYTICS")
        self.assertEqual(first["stages"][-1]["reconciliation"]["difference_eur"], "0.00")
        self.assertEqual(first["stages"][-1]["replay"]["duplicate_imports"], 0)


if __name__ == "__main__":
    unittest.main()
