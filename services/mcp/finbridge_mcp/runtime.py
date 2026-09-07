"""Deterministic PASS 5 runtime factory."""

from __future__ import annotations

import os

from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_processing import ProcessingOrchestrator
from finbridge_storage import build_azurite_storage, build_in_memory_storage

from .operations import OperationsService


def build_seeded_operations_service() -> OperationsService:
    """Create a read-only operations service over a completed persisted golden path.

    Default mode uses the exact storage adapter code with an in-memory blob backend. Set
    FINBRIDGE_MCP_STORAGE=azurite to point the same operations layer at a real Azurite instance.
    """

    mode = os.environ.get("FINBRIDGE_MCP_STORAGE", "memory").strip().lower()
    if mode == "memory":
        storage = build_in_memory_storage()
    elif mode == "azurite":
        connection = os.environ.get("FINBRIDGE_STORAGE", "UseDevelopmentStorage=true")
        storage = build_azurite_storage(connection)
    else:
        raise RuntimeError(f"Unsupported FINBRIDGE_MCP_STORAGE mode: {mode}")
    batch = build_synthetic_legacy_batch()
    # Idempotent even if the Azurite evidence already exists from a prior run.
    ProcessingOrchestrator(storage).run_golden_path(batch)
    return OperationsService(storage)
