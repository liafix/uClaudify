from dataclasses import replace
from decimal import Decimal
import unittest

from finbridge_domain.invariants import (
    FinancialInvariantError,
    assert_fin_01_accepted_once,
    assert_fin_02_no_duplicate_verified,
    assert_fin_03_record_accountability,
    assert_fin_04_reconciliation_from_accepted,
    reconcile_accepted_records,
)
from finbridge_domain.ledger import InMemoryBatchLedger
from finbridge_domain.models import Transaction


def tx(
    transaction_id: str,
    source_line: int,
    amount: str,
    direction: str = "CREDIT",
) -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        account_id="ACC-001",
        booking_date="2026-09-05",
        amount=Decimal(amount),
        currency="EUR",
        direction=direction,  # type: ignore[arg-type]
        counterparty="Synthetic Counterparty",
        source_system="AlpineBank Legacy Finance",
        source_line=source_line,
    )


class Pass2FinancialInvariantTests(unittest.TestCase):
    def test_fin_01_accepted_source_record_can_be_counted_only_once(self) -> None:
        first = tx("TX-A", 2, "10.00")
        duplicated_source_row = replace(first, transaction_id="TX-B")
        with self.assertRaises(FinancialInvariantError):
            assert_fin_01_accepted_once((first, duplicated_source_row))

    def test_fin_02_duplicate_transaction_id_never_enters_verified_dataset(self) -> None:
        accepted = (tx("TX-A", 2, "10.00"), tx("TX-A", 3, "15.00"))
        with self.assertRaises(FinancialInvariantError):
            assert_fin_02_no_duplicate_verified(accepted)

    def test_fin_03_every_input_row_has_exactly_one_outcome(self) -> None:
        a = tx("TX-A", 2, "10.00")
        b = tx("TX-B", 3, "15.00")
        assert_fin_03_record_accountability((a, b), (a,), (b,))

        with self.assertRaises(FinancialInvariantError):
            assert_fin_03_record_accountability((a, b), (a,), ())
        with self.assertRaises(FinancialInvariantError):
            assert_fin_03_record_accountability((a, b), (a, b), (b,))

    def test_fin_04_reconciliation_is_derived_only_from_accepted_records(self) -> None:
        accepted = (
            tx("TX-C", 2, "100.00", "CREDIT"),
            tx("TX-D", 3, "25.00", "DEBIT"),
        )
        quarantined = tx("TX-Q", 4, "999999.00", "CREDIT")
        result = reconcile_accepted_records(
            accepted,
            opening_balance_eur=Decimal("1000.00"),
            expected_closing_balance_eur=Decimal("1075.00"),
        )
        self.assertEqual(result.credits_eur, Decimal("100.00"))
        self.assertEqual(result.debits_eur, Decimal("25.00"))
        self.assertEqual(result.calculated_closing_balance_eur, Decimal("1075.00"))
        self.assertNotEqual(result.credits_eur, quarantined.amount)
        assert_fin_04_reconciliation_from_accepted(accepted, result)

        tampered = replace(result, credits_eur=Decimal("1000099.00"))
        with self.assertRaises(FinancialInvariantError):
            assert_fin_04_reconciliation_from_accepted(accepted, tampered)

    def test_fin_05_replay_keeps_exactly_one_persisted_dataset(self) -> None:
        batch = (tx("TX-A", 2, "10.00"),)
        ledger = InMemoryBatchLedger()
        ledger.commit("BATCH-1", batch, accepted_count=1, quarantine_count=0)
        self.assertEqual(ledger.dataset_count, 1)
        ledger.replay("BATCH-1", batch)
        ledger.replay("BATCH-1", batch)
        self.assertEqual(ledger.dataset_count, 1)


if __name__ == "__main__":
    unittest.main()
