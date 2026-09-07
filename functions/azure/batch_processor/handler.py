"""Framework-free core invoked by the Azure Function trigger adapter."""

from __future__ import annotations

from typing import Any

from finbridge_domain.contracts import FROZEN_SCENARIO
from finbridge_storage.ports import StorageBundle
from finbridge_storage.serialization import batch_from_bytes
from finbridge_processing import ProcessingOrchestrator


def process_raw_blob(payload: bytes, storage: StorageBundle) -> dict[str, Any]:
    batch_id, rows = batch_from_bytes(payload)
    if batch_id != FROZEN_SCENARIO.batch_id:
        raise ValueError(f"Unexpected synthetic batch id: {batch_id}")
    # Azure Blob has already persisted the raw object before the trigger fires. The orchestrator
    # validates that persisted evidence matches the trigger payload and never redefines domain rules.
    return ProcessingOrchestrator(storage).run_golden_path(rows, raw_already_persisted=True)
