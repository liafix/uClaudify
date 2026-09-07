from decimal import Decimal
import unittest

from finbridge_domain.contracts import (
    CANONICAL_TRANSACTION_FIELDS,
    CANDIDATE_DISCLAIMER,
    FINANCIAL_INVARIANTS,
    FROZEN_SCENARIO,
    GoldenState,
    PROHIBITED_SCOPE,
    QUALITY_RULES,
)


class FrozenContractTests(unittest.TestCase):
    def test_scenario_counts_are_exact_and_accounted(self) -> None:
        self.assertEqual(FROZEN_SCENARIO.input_records, 1024)
        self.assertEqual(FROZEN_SCENARIO.accepted_records, 1019)
        self.assertEqual(FROZEN_SCENARIO.duplicate_records, 3)
        self.assertEqual(FROZEN_SCENARIO.invalid_currency_records, 2)
        self.assertEqual(FROZEN_SCENARIO.quarantined_records, 5)
        self.assertEqual(FROZEN_SCENARIO.unaccounted_records, 0)
        self.assertEqual(FROZEN_SCENARIO.accounted_records, FROZEN_SCENARIO.input_records)

    def test_financial_control_total_is_exact_decimal(self) -> None:
        self.assertIsInstance(FROZEN_SCENARIO.opening_balance_eur, Decimal)
        self.assertEqual(
            FROZEN_SCENARIO.calculated_closing_balance_eur,
            FROZEN_SCENARIO.expected_closing_balance_eur,
        )
        self.assertEqual(FROZEN_SCENARIO.expected_closing_balance_eur, Decimal("1026700.00"))

    def test_canonical_transaction_contract_is_frozen(self) -> None:
        self.assertEqual(
            CANONICAL_TRANSACTION_FIELDS,
            (
                "transaction_id",
                "account_id",
                "booking_date",
                "amount",
                "currency",
                "direction",
                "counterparty",
                "source_system",
            ),
        )

    def test_rule_sets_are_complete(self) -> None:
        self.assertEqual(tuple(QUALITY_RULES), ("DQ-01", "DQ-02", "DQ-03", "DQ-04", "DQ-05"))
        self.assertEqual(
            tuple(FINANCIAL_INVARIANTS),
            ("FIN-01", "FIN-02", "FIN-03", "FIN-04", "FIN-05"),
        )

    def test_golden_state_order_is_frozen(self) -> None:
        self.assertEqual(
            [state.value for state in GoldenState],
            [
                "RECEIVED",
                "INGESTION_PASS",
                "SCHEMA_PASS",
                "NORMALIZATION_PASS",
                "QUALITY_BLOCKED",
                "QUARANTINED",
                "RECONCILED",
                "IDEMPOTENCY_PASS",
                "READY_FOR_ANALYTICS",
            ],
        )

    def test_candidate_safety_contract_is_explicit(self) -> None:
        self.assertIn("AlpineBank is fictional", CANDIDATE_DISCLAIMER)
        self.assertIn("live LLM dependency for the golden path", PROHIBITED_SCOPE)
        self.assertIn("uCloudify proprietary data or code", PROHIBITED_SCOPE)


if __name__ == "__main__":
    unittest.main()
