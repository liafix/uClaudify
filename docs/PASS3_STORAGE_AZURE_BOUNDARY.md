# PASS 3 — Storage + Azure-compatible processing boundary

## Goal

Persist the already-proven FinBridge golden path without moving finance decisions into cloud or
storage framework code. PASS 3 introduces exactly four durable surfaces:

- `raw` — immutable received batch evidence,
- `processed` — immutable accepted/verified records,
- `quarantine` — rejected source records plus their DQ issue,
- `audit` — state evidence plus the persisted DQ-05 / FIN-05 batch commit.

## Boundary rule

`finbridge_domain` remains framework-free. `ProcessingOrchestrator` sequences persistence around the
existing `GoldenPathPipeline`. Azure Functions never import DQ rules, reconciliation functions or the
domain pipeline directly; the trigger calls the orchestration handler only.

## Golden path persistence

The persisted execution must remain evidence-identical to PASS 1/2:

`1,024 raw -> QUALITY_BLOCKED -> 1,019 accepted + 5 anomalies -> 5 quarantine -> €0.00 reconciliation -> exact replay -> READY_FOR_ANALYTICS`

After a process restart against the same store, exact replay must still leave exactly one commit and
one processed dataset.

## Azure / Azurite implementation

The Blob adapter uses `azure-storage-blob` lazily and accepts either a normal Azure Storage connection
string or `UseDevelopmentStorage=true` for Azurite. The same `BlobRawBatchStore`,
`BlobProcessedBatchStore`, `BlobQuarantineStore` and `BlobAuditStore` are used in both modes.

Local Azurite infrastructure is defined under `infra/azurite/`. A real-service smoke is provided in
`scripts/pass3_azurite_smoke.py` and is executed by PASS 3 CI with Azurite running.

## Azure Function

`functions/azure/function_app.py` is a Python v2 Blob trigger on `raw/{name}`. It contains wiring only.
The framework-free `batch_processor.handler.process_raw_blob()` validates that the trigger payload
matches the immutable raw evidence and delegates to `ProcessingOrchestrator`.

## Explicit non-goals

PASS 3 does not add the real Java mapping/export adapter (PASS 4), MCP/AI operations (PASS 5), or
Terraform production resource hardening (PASS 6).
