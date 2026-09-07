"""Frozen candidate-demo domain contract.

PASS 0 deliberately contains contracts and invariants only. Processing behavior is implemented in
later passes. Any change to the constants in this module after PASS 0 requires an explicit contract
review because the recruitment story and golden-path tests will bind to them.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class GoldenState(StrEnum):
    RECEIVED = "RECEIVED"
    INGESTION_PASS = "INGESTION_PASS"
    SCHEMA_PASS = "SCHEMA_PASS"
    NORMALIZATION_PASS = "NORMALIZATION_PASS"
    QUALITY_BLOCKED = "QUALITY_BLOCKED"
    QUARANTINED = "QUARANTINED"
    RECONCILED = "RECONCILED"
    IDEMPOTENCY_PASS = "IDEMPOTENCY_PASS"
    READY_FOR_ANALYTICS = "READY_FOR_ANALYTICS"


CANONICAL_TRANSACTION_FIELDS: tuple[str, ...] = (
    "transaction_id",
    "account_id",
    "booking_date",
    "amount",
    "currency",
    "direction",
    "counterparty",
    "source_system",
)

QUALITY_RULES: dict[str, str] = {
    "DQ-01": "transaction_id must be unique within a batch",
    "DQ-02": "currency must be an allowed ISO-style currency code",
    "DQ-03": "amount must be a valid Decimal-compatible monetary value",
    "DQ-04": "required canonical fields must not be empty",
    "DQ-05": "retrying the same batch must not create a second import",
}

FINANCIAL_INVARIANTS: dict[str, str] = {
    "FIN-01": "every accepted record is counted exactly once",
    "FIN-02": "duplicate input never enters the verified dataset",
    "FIN-03": "every input record has an explicit accepted or quarantined outcome",
    "FIN-04": "reconciliation is derived only from accepted records",
    "FIN-05": "replaying the same batch creates no second dataset",
}

PROHIBITED_SCOPE: tuple[str, ...] = (
    "real bank/customer data",
    "uCloudify proprietary data or code",
    "authentication/user management",
    "live LLM dependency for the golden path",
    "arbitrary SQL tool access",
    "arbitrary shell execution from AI",
    "Kubernetes/Kafka/Databricks/Snowflake in MVP",
    "C# or Scala in MVP",
)

CANDIDATE_DISCLAIMER = (
    "AlpineBank is fictional. No uCloudify client data, internal repositories, proprietary "
    "architecture, production credentials, or confidential processes are represented or used."
)


@dataclass(frozen=True, slots=True)
class ScenarioContract:
    batch_id: str
    source_system: str
    input_records: int
    accepted_records: int
    duplicate_records: int
    invalid_currency_records: int
    quarantined_records: int
    unaccounted_records: int
    opening_balance_eur: Decimal
    credits_eur: Decimal
    debits_eur: Decimal
    expected_closing_balance_eur: Decimal

    @property
    def accounted_records(self) -> int:
        return self.accepted_records + self.quarantined_records

    @property
    def calculated_closing_balance_eur(self) -> Decimal:
        return self.opening_balance_eur + self.credits_eur - self.debits_eur


FROZEN_SCENARIO = ScenarioContract(
    batch_id="2026-09-05-001",
    source_system="AlpineBank Legacy Finance",
    input_records=1024,
    accepted_records=1019,
    duplicate_records=3,
    invalid_currency_records=2,
    quarantined_records=5,
    unaccounted_records=0,
    opening_balance_eur=Decimal("1000000.00"),
    credits_eur=Decimal("125400.00"),
    debits_eur=Decimal("98700.00"),
    expected_closing_balance_eur=Decimal("1026700.00"),
)
