# Architecture Boundaries — PASS 0

## Python

Primary engineering surface. Future passes place ingestion, validation, transformation, quarantine, reconciliation, idempotency and MCP read-only operations here.

## Java

Compatibility adapter for the fictional legacy finance source. It may map legacy records into the canonical contract, but does not own data-quality or finance decisions.

## Azure

Optional real cloud mode. The local candidate demo must remain deterministic without Azure credentials.

## Terraform

Reproducible infrastructure contract. No manual cloud-only architecture should be necessary to understand the project.

## Candidate web app

Presentation layer only. It may trigger candidate-demo actions and visualize evidence, but it cannot manufacture domain pass/fail state.

## AI / MCP

Future read-only explanation surface. Tools must be scoped and evidence-bearing. No arbitrary database query or shell execution tool belongs in the MVP.

## PASS 3 storage / processing boundary

Storage is outside the finance domain. `RawBatchStore`, `ProcessedBatchStore`, `QuarantineStore` and
`AuditStore` persist immutable evidence; they do not decide whether a record is valid or whether a
batch reconciles. `ProcessingOrchestrator` sequences the existing domain pipeline around those ports.

The same Blob-store implementation runs over an in-memory backend for deterministic candidate tests
and over Azure Blob Storage/Azurite via `AzureBlobBackend`. Azure Functions remain a trigger adapter
only.
