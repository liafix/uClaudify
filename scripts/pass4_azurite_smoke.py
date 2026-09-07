#!/usr/bin/env python3
"""Real Java-origin canonical batch -> Python domain -> Azurite PASS 4 smoke."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for relative in ("services/domain", "services/storage", "services/processing"):
    sys.path.insert(0, str(ROOT / relative))

from finbridge_domain.contracts import FROZEN_SCENARIO  # noqa: E402
from finbridge_domain.golden_path import run_golden_path  # noqa: E402
from finbridge_processing import ProcessingOrchestrator, load_canonical_csv  # noqa: E402
from finbridge_storage.factory import build_azurite_storage  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: pass4_azurite_smoke.py <java-canonical.csv>")
    batch = load_canonical_csv(sys.argv[1])
    connection = os.environ.get("FINBRIDGE_STORAGE", "UseDevelopmentStorage=true")
    storage = build_azurite_storage(connection)
    runtime = ProcessingOrchestrator(storage).run_golden_path(batch)
    if runtime != run_golden_path():
        raise AssertionError("Java-origin Azurite execution diverged from frozen candidate evidence")
    if len(storage.raw.get(FROZEN_SCENARIO.batch_id) or ()) != 1024:
        raise AssertionError("Azurite raw surface did not persist Java-origin 1,024 records")
    if len(storage.processed.get(FROZEN_SCENARIO.batch_id) or ()) != 1019:
        raise AssertionError("Azurite processed surface did not persist 1,019 accepted records")
    quarantine = storage.quarantine.get(FROZEN_SCENARIO.batch_id)
    if quarantine is None or len(quarantine[0]) != 5 or len(quarantine[1]) != 5:
        raise AssertionError("Azurite quarantine did not persist five Java-origin anomalies")
    if storage.audit.count_commits() != 1:
        raise AssertionError("Java-origin run did not preserve exactly one dataset")
    replay = ProcessingOrchestrator(storage).run_golden_path(batch)
    if replay != runtime or storage.audit.count_commits() != 1:
        raise AssertionError("Java-origin replay is not idempotent")
    print("PASS 4 real Java -> Python -> Azurite golden path: PASS")


if __name__ == "__main__":
    main()
