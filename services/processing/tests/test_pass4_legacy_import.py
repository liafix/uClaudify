from __future__ import annotations

import csv
import io
import unittest

from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_processing.legacy_import import LegacyImportError, parse_canonical_csv


class Pass4LegacyImportTests(unittest.TestCase):
    def _csv_from_python_fixture(self) -> str:
        out = io.StringIO(newline="")
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(
            (
                "transaction_id",
                "account_id",
                "booking_date",
                "amount",
                "currency",
                "direction",
                "counterparty",
                "source_system",
            )
        )
        for row in build_synthetic_legacy_batch():
            writer.writerow(
                (
                    row.transaction_id,
                    row.account_id,
                    row.booking_date,
                    f"{row.amount:.2f}",
                    row.currency,
                    row.direction,
                    row.counterparty,
                    row.source_system,
                )
            )
        return out.getvalue()

    def test_header_mismatch_fails_closed(self) -> None:
        text = self._csv_from_python_fixture().replace("transaction_id", "legacy_id", 1)
        with self.assertRaises(LegacyImportError):
            parse_canonical_csv(text)

    def test_structural_import_preserves_python_fixture_semantics(self) -> None:
        imported = parse_canonical_csv(self._csv_from_python_fixture())
        expected = build_synthetic_legacy_batch()
        self.assertEqual(imported, expected)


if __name__ == "__main__":
    unittest.main()
