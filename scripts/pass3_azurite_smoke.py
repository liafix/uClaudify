#!/usr/bin/env python3
"""Real Azurite integration smoke. Requires Azure SDK + a running Azurite service."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for relative in ("services/domain", "services/storage", "services/processing"):
    sys.path.insert(0, str(ROOT / relative))

from finbridge_domain.contracts import FROZEN_SCENARIO  # noqa: E402
from finbridge_domain.fixtures import build_synthetic_legacy_batch  # noqa: E402
from finbridge_domain.golden_path import run_golden_path  # noqa: E402
from finbridge_processing import ProcessingOrchestrator  # noqa: E402
from finbridge_storage.factory import build_azurite_storage  # noqa: E402


def main() -> None:
    connection = os.environ.get("FINBRIDGE_STORAGE", "UseDevelopmentStorage=true")
    storage = build_azurite_storage(connection)
    runtime = ProcessingOrchestrator(storage).run_golden_path(build_synthetic_legacy_batch())
    if runtime != run_golden_path():
        raise AssertionError("Azurite-backed execution diverged from in-memory golden evidence")
    if len(storage.raw.get(FROZEN_SCENARIO.batch_id) or ()) != 1024:
        raise AssertionError("Azurite raw surface did not persist all 1,024 records")
    if len(storage.processed.get(FROZEN_SCENARIO.batch_id) or ()) != 1019:
        raise AssertionError("Azurite processed surface did not persist 1,019 accepted records")
    quarantine = storage.quarantine.get(FROZEN_SCENARIO.batch_id)
    if quarantine is None or len(quarantine[0]) != 5 or len(quarantine[1]) != 5:
        raise AssertionError("Azurite quarantine surface did not persist five accountable anomalies")
    if storage.audit.count_commits() != 1:
        raise AssertionError("Azurite audit ledger did not preserve exactly one committed dataset")

    # New process/orchestrator instance against the same durable store must remain idempotent.
    replay = ProcessingOrchestrator(storage).run_golden_path(build_synthetic_legacy_batch())
    if replay != runtime or storage.audit.count_commits() != 1:
        raise AssertionError("Azurite persisted replay is not idempotent")
    print("PASS 3 real Azurite storage + restart-idempotency smoke: PASS")


if __name__ == "__main__":
    main()
