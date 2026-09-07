"""PASS 2 hardened golden-path pipeline.

The candidate story remains local and deterministic, but the quality and finance decisions are now
backed by explicit reusable rule/invariant engines. Azure/storage abstractions remain PASS 3 scope.
"""

from __future__ import annotations

from .contracts import FROZEN_SCENARIO, GoldenState
from .invariants import (
    assert_fin_01_accepted_once,
    assert_fin_02_no_duplicate_verified,
    assert_fin_03_record_accountability,
    assert_fin_04_reconciliation_from_accepted,
    reconcile_accepted_records,
)
from .ledger import BatchLedger, InMemoryBatchLedger
from .models import PipelineSnapshot, ReconciliationResult, ReplayResult, Transaction, ValidationIssue
from .rules import DataQualityEngine


class InvalidTransitionError(RuntimeError):
    """Raised when the candidate-demo state machine is advanced out of order."""


class GoldenPathPipeline:
    def __init__(
        self,
        batch: tuple[Transaction, ...],
        *,
        ledger: BatchLedger | None = None,
    ) -> None:
        if len(batch) != FROZEN_SCENARIO.input_records:
            raise ValueError("PASS 2 requires the exact frozen 1,024-row synthetic batch")
        self._batch = batch
        self._state = GoldenState.RECEIVED
        self._accepted: tuple[Transaction, ...] = ()
        self._issues: tuple[ValidationIssue, ...] = ()
        self._quarantined: tuple[Transaction, ...] = ()
        self._reconciliation: ReconciliationResult | None = None
        self._replay: ReplayResult | None = None
        self._ledger = ledger or InMemoryBatchLedger()
        self._quality_engine = DataQualityEngine()
        self._history: list[GoldenState] = [GoldenState.RECEIVED]

    @property
    def state(self) -> GoldenState:
        return self._state

    @property
    def history(self) -> tuple[GoldenState, ...]:
        return tuple(self._history)

    @property
    def accepted(self) -> tuple[Transaction, ...]:
        return self._accepted

    @property
    def quarantined(self) -> tuple[Transaction, ...]:
        return self._quarantined

    @property
    def issues(self) -> tuple[ValidationIssue, ...]:
        return self._issues

    @property
    def ledger_dataset_count(self) -> int:
        return self._ledger.dataset_count

    def snapshot(self) -> PipelineSnapshot:
        quarantined = len(self._quarantined)
        accepted = len(self._accepted)
        if self._state is GoldenState.QUALITY_BLOCKED:
            # The five anomalous source rows have a deterministic classification, but quarantine is
            # still an explicit operator step in the candidate demo.
            unaccounted = len(self._batch) - accepted - len(self._issues)
        elif self._state in {
            GoldenState.QUARANTINED,
            GoldenState.RECONCILED,
            GoldenState.IDEMPOTENCY_PASS,
            GoldenState.READY_FOR_ANALYTICS,
        }:
            unaccounted = len(self._batch) - accepted - quarantined
        else:
            unaccounted = len(self._batch)
        return PipelineSnapshot(
            state=self._state,
            input_records=len(self._batch),
            accepted_records=accepted,
            anomaly_records=len(self._issues),
            quarantined_records=quarantined,
            unaccounted_records=unaccounted,
            issues=self._issues,
            reconciliation=self._reconciliation,
            replay=self._replay,
        )

    def _advance(self, state: GoldenState) -> None:
        self._state = state
        self._history.append(state)

    def process_to_quality_gate(self) -> PipelineSnapshot:
        if self._state is not GoldenState.RECEIVED:
            raise InvalidTransitionError("Batch processing can only start from RECEIVED")

        self._advance(GoldenState.INGESTION_PASS)
        self._advance(GoldenState.SCHEMA_PASS)
        self._advance(GoldenState.NORMALIZATION_PASS)

        validation = self._quality_engine.validate(self._batch)
        self._accepted = validation.accepted
        self._issues = validation.issues

        if not self._issues:
            raise AssertionError("Frozen PASS 2 scenario must initially fail the data-quality gate")
        if len(self._accepted) != FROZEN_SCENARIO.accepted_records:
            raise AssertionError("Accepted record count diverged from frozen contract")
        if len(self._issues) != FROZEN_SCENARIO.quarantined_records:
            raise AssertionError("Anomaly count diverged from frozen contract")

        # FIN-01 and FIN-02 are meaningful immediately at the verified-candidate boundary.
        assert_fin_01_accepted_once(self._accepted)
        assert_fin_02_no_duplicate_verified(self._accepted)

        self._advance(GoldenState.QUALITY_BLOCKED)
        return self.snapshot()

    def quarantine_invalid_records(self) -> PipelineSnapshot:
        if self._state is not GoldenState.QUALITY_BLOCKED:
            raise InvalidTransitionError("Quarantine requires QUALITY_BLOCKED")

        issue_lines = {issue.source_line for issue in self._issues}
        self._quarantined = tuple(row for row in self._batch if row.source_line in issue_lines)
        if len(self._quarantined) != FROZEN_SCENARIO.quarantined_records:
            raise AssertionError("Quarantine count diverged from frozen contract")

        assert_fin_03_record_accountability(self._batch, self._accepted, self._quarantined)

        self._advance(GoldenState.QUARANTINED)
        return self.snapshot()

    def reconcile(self) -> PipelineSnapshot:
        if self._state is not GoldenState.QUARANTINED:
            raise InvalidTransitionError("Reconciliation requires QUARANTINED")

        self._reconciliation = reconcile_accepted_records(
            self._accepted,
            opening_balance_eur=FROZEN_SCENARIO.opening_balance_eur,
            expected_closing_balance_eur=FROZEN_SCENARIO.expected_closing_balance_eur,
        )
        assert_fin_04_reconciliation_from_accepted(self._accepted, self._reconciliation)

        if self._reconciliation.credits_eur != FROZEN_SCENARIO.credits_eur:
            raise AssertionError("FIN-04 violated: accepted credit total diverged")
        if self._reconciliation.debits_eur != FROZEN_SCENARIO.debits_eur:
            raise AssertionError("FIN-04 violated: accepted debit total diverged")
        if not self._reconciliation.reconciled:
            raise AssertionError("Reconciliation difference must be exactly €0.00")

        # Commit once only after finance evidence is clean. The ledger becomes the executable DQ-05
        # / FIN-05 boundary that PASS 3 will later persist behind a storage interface.
        self._ledger.commit(
            FROZEN_SCENARIO.batch_id,
            self._batch,
            accepted_count=len(self._accepted),
            quarantine_count=len(self._quarantined),
        )
        if self._ledger.dataset_count != 1:
            raise AssertionError("FIN-05 violated: exactly one dataset must exist after commit")

        self._advance(GoldenState.RECONCILED)
        return self.snapshot()

    def replay_batch(self) -> PipelineSnapshot:
        if self._state is not GoldenState.RECONCILED:
            raise InvalidTransitionError("Replay check requires RECONCILED")

        before = self._ledger.dataset_count
        self._replay = self._ledger.replay(FROZEN_SCENARIO.batch_id, self._batch)
        after = self._ledger.dataset_count

        if before != 1 or after != 1:
            raise AssertionError("FIN-05 violated: replay created a second dataset")
        if any(
            (
                self._replay.new_accepted_records,
                self._replay.duplicate_imports,
                self._replay.additional_quarantine_rows,
            )
        ):
            raise AssertionError("DQ-05 violated: exact replay created new import effects")

        self._advance(GoldenState.IDEMPOTENCY_PASS)
        return self.snapshot()

    def confirm_analytics_readiness(self) -> PipelineSnapshot:
        if self._state is not GoldenState.IDEMPOTENCY_PASS:
            raise InvalidTransitionError("Analytics readiness requires IDEMPOTENCY_PASS")
        if self._reconciliation is None or not self._reconciliation.reconciled:
            raise AssertionError("Reconciliation evidence is missing")
        if self._replay is None or any(
            (
                self._replay.new_accepted_records,
                self._replay.duplicate_imports,
                self._replay.additional_quarantine_rows,
            )
        ):
            raise AssertionError("Idempotency evidence is not clean")
        assert_fin_01_accepted_once(self._accepted)
        assert_fin_02_no_duplicate_verified(self._accepted)
        assert_fin_03_record_accountability(self._batch, self._accepted, self._quarantined)
        assert_fin_04_reconciliation_from_accepted(self._accepted, self._reconciliation)
        if self._ledger.dataset_count != 1:
            raise AssertionError("FIN-05 violated: final dataset cardinality is not exactly one")

        self._advance(GoldenState.READY_FOR_ANALYTICS)
        return self.snapshot()
