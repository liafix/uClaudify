from decimal import Decimal
import unittest

from finbridge_domain.ledger import BatchConflictError, InMemoryBatchLedger
from finbridge_domain.models import RawTransactionRecord, Transaction
from finbridge_domain.rules import DataQualityEngine


def raw(
    *,
    transaction_id: str | None = "TX-00001",
    account_id: str | None = "ACC-001",
    booking_date: str | None = "2026-09-05",
    amount: object = "10.25",
    currency: str | None = "EUR",
    direction: str | None = "CREDIT",
    counterparty: str | None = "Synthetic Counterparty",
    source_system: str | None = "AlpineBank Legacy Finance",
    source_line: int = 2,
) -> RawTransactionRecord:
    return RawTransactionRecord(
        transaction_id=transaction_id,
        account_id=account_id,
        booking_date=booking_date,
        amount=amount,
        currency=currency,
        direction=direction,
        counterparty=counterparty,
        source_system=source_system,
        source_line=source_line,
    )


def tx(*, transaction_id: str = "TX-00001", source_line: int = 2) -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        account_id="ACC-001",
        booking_date="2026-09-05",
        amount=Decimal("10.25"),
        currency="EUR",
        direction="CREDIT",
        counterparty="Synthetic Counterparty",
        source_system="AlpineBank Legacy Finance",
        source_line=source_line,
    )


class Pass2DataQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = DataQualityEngine()

    def test_dq_01_duplicate_transaction_id_is_blocked(self) -> None:
        result = self.engine.validate(
            [
                raw(transaction_id="TX-DUP", source_line=2),
                raw(transaction_id="TX-DUP", source_line=3),
            ]
        )
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(len(result.issues), 1)
        self.assertEqual(result.issues[0].rule, "DQ-01")
        self.assertEqual(result.issues[0].reason, "DUPLICATE_TRANSACTION")

    def test_dq_02_invalid_currency_is_blocked(self) -> None:
        result = self.engine.validate([raw(currency="EURO")])
        self.assertEqual(result.accepted, ())
        self.assertEqual(result.issues[0].rule, "DQ-02")
        self.assertEqual(result.issues[0].reason, "INVALID_CURRENCY:EURO")

    def test_dq_03_non_decimal_compatible_amount_is_blocked(self) -> None:
        for amount in ("not-money", float("nan"), 10.25):
            with self.subTest(amount=amount):
                result = self.engine.validate([raw(amount=amount)])
                self.assertEqual(result.accepted, ())
                self.assertEqual(result.issues[0].rule, "DQ-03")
                self.assertEqual(result.issues[0].reason, "INVALID_AMOUNT")

    def test_dq_03_decimal_string_normalizes_exactly(self) -> None:
        result = self.engine.validate([raw(amount="10.25")])
        self.assertEqual(len(result.accepted), 1)
        self.assertIsInstance(result.accepted[0].amount, Decimal)
        self.assertEqual(result.accepted[0].amount, Decimal("10.25"))

    def test_dq_04_each_required_field_is_fail_closed(self) -> None:
        required = (
            "transaction_id",
            "account_id",
            "booking_date",
            "currency",
            "direction",
            "counterparty",
            "source_system",
        )
        for field in required:
            with self.subTest(field=field):
                kwargs = {field: ""}
                result = self.engine.validate([raw(**kwargs)])
                self.assertEqual(result.accepted, ())
                self.assertEqual(result.issues[0].rule, "DQ-04")
                self.assertEqual(result.issues[0].reason, f"REQUIRED_FIELD_EMPTY:{field}")

    def test_dq_05_exact_retry_has_zero_new_import_effects(self) -> None:
        ledger = InMemoryBatchLedger()
        batch = (tx(),)
        ledger.commit("BATCH-1", batch, accepted_count=1, quarantine_count=0)
        replay = ledger.replay("BATCH-1", batch)
        self.assertTrue(replay.previously_processed)
        self.assertEqual(replay.new_accepted_records, 0)
        self.assertEqual(replay.duplicate_imports, 0)
        self.assertEqual(replay.additional_quarantine_rows, 0)
        self.assertEqual(ledger.dataset_count, 1)


    def test_dq_05_same_payload_with_changed_outcome_counts_fails_closed(self) -> None:
        ledger = InMemoryBatchLedger()
        batch = (tx(),)
        ledger.commit("BATCH-1", batch, accepted_count=1, quarantine_count=0)
        with self.assertRaises(BatchConflictError):
            ledger.commit("BATCH-1", batch, accepted_count=0, quarantine_count=1)
        self.assertEqual(ledger.dataset_count, 1)

    def test_dq_05_same_batch_id_with_changed_payload_fails_closed(self) -> None:
        ledger = InMemoryBatchLedger()
        ledger.commit("BATCH-1", (tx(transaction_id="TX-A"),), accepted_count=1, quarantine_count=0)
        with self.assertRaises(BatchConflictError):
            ledger.replay("BATCH-1", (tx(transaction_id="TX-B"),))
        self.assertEqual(ledger.dataset_count, 1)


if __name__ == "__main__":
    unittest.main()
