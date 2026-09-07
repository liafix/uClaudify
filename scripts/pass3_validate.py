#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for relative in ("services/domain", "services/storage", "services/processing", "functions/azure"):
    sys.path.insert(0, str(ROOT / relative))

from finbridge_domain.contracts import FROZEN_SCENARIO  # noqa: E402
from finbridge_domain.fixtures import build_synthetic_legacy_batch  # noqa: E402
from finbridge_domain.golden_path import run_golden_path  # noqa: E402
from finbridge_processing import ProcessingOrchestrator  # noqa: E402
from finbridge_storage import build_in_memory_storage  # noqa: E402

REQUIRED_PATHS = (
    "services/storage/finbridge_storage/ports.py",
    "services/storage/finbridge_storage/blob_backend.py",
    "services/storage/finbridge_storage/blob_stores.py",
    "services/storage/finbridge_storage/factory.py",
    "services/processing/finbridge_processing/orchestrator.py",
    "services/processing/finbridge_processing/storage_ledger.py",
    "functions/azure/function_app.py",
    "functions/azure/batch_processor/handler.py",
    "functions/azure/host.json",
    "functions/azure/local.settings.example.json",
    "functions/azure/requirements.txt",
    "infra/azurite/docker-compose.yml",
    "scripts/pass3_azurite_smoke.py",
    "docs/PASS3_STORAGE_AZURE_BOUNDARY.md",
)


def main() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f"Missing PASS 3 artifacts: {missing}")

    storage = build_in_memory_storage()
    batch = build_synthetic_legacy_batch()
    runtime = ProcessingOrchestrator(storage).run_golden_path(batch)
    if runtime != run_golden_path():
        raise AssertionError("Storage-backed processing changed the frozen candidate golden path")

    if len(storage.raw.get(FROZEN_SCENARIO.batch_id) or ()) != 1024:
        raise AssertionError("Raw storage did not persist all 1,024 source records")
    if len(storage.processed.get(FROZEN_SCENARIO.batch_id) or ()) != 1019:
        raise AssertionError("Processed storage did not persist exactly 1,019 accepted records")
    quarantine = storage.quarantine.get(FROZEN_SCENARIO.batch_id)
    if quarantine is None or len(quarantine[0]) != 5 or len(quarantine[1]) != 5:
        raise AssertionError("Quarantine storage did not persist five records + five issues")
    if storage.audit.count_commits() != 1:
        raise AssertionError("Storage-backed FIN-05 ledger must have one committed dataset")

    events = storage.audit.list_events(FROZEN_SCENARIO.batch_id)
    expected_events = (
        "RECEIVED",
        "QUALITY_BLOCKED",
        "QUARANTINED",
        "RECONCILED",
        "IDEMPOTENCY_PASS",
        "READY_FOR_ANALYTICS",
    )
    if tuple(event.event_type for event in events) != expected_events:
        raise AssertionError("Audit event sequence diverged from the frozen golden path")

    second = ProcessingOrchestrator(storage).run_golden_path(batch)
    if second != runtime or storage.audit.count_commits() != 1:
        raise AssertionError("Restart replay created divergent evidence or a second dataset")

    function_source = (ROOT / "functions/azure/function_app.py").read_text(encoding="utf-8")
    handler_source = (ROOT / "functions/azure/batch_processor/handler.py").read_text(encoding="utf-8")
    forbidden = ("DataQualityEngine", "reconcile_accepted_records", "GoldenPathPipeline")
    if any(token in function_source or token in handler_source for token in forbidden):
        raise AssertionError("Azure Function boundary contains domain decision logic")

    compose = (ROOT / "infra/azurite/docker-compose.yml").read_text(encoding="utf-8")
    if "azurite" not in compose.lower() or "10000:10000" not in compose:
        raise AssertionError("Azurite local infrastructure contract is incomplete")

    current_pass = int((ROOT / "contracts/current_pass.txt").read_text().strip())
    if current_pass <= 3 and (ROOT / "services/mcp").exists():
        raise AssertionError("PASS 5 MCP scope leaked into a PASS 3 artifact")

    print("PASS: raw/processed/quarantine/audit storage ports are implemented")
    print("PASS: storage-backed golden path is evidence-identical to PASS 1/2")
    print("PASS: 1,024 raw / 1,019 processed / 5 quarantine / 1 commit persisted")
    print("PASS: process restart preserves DQ-05 / FIN-05 exactly-one semantics")
    print("PASS: Azure Function is a thin orchestration trigger boundary")
    print("PASS: Azurite adapter + real-service smoke script are present")
    print("PASS 3 storage + Azure-compatible boundary validation: PASS")


if __name__ == "__main__":
    main()
