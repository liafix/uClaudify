# PASS 5 — Read-only MCP operations + controlled AI evidence

PASS 5 adds an observation layer above the already-verified Java -> Python -> storage pipeline. It
**does not** create a second data-quality or finance decision engine.

## Frozen read-only MCP tools

1. `get_batch_status(batch_id)`
2. `get_data_quality_summary(batch_id)`
3. `list_batch_anomalies(batch_id)`
4. `trace_transaction(batch_id, transaction_id)`
5. `get_reconciliation_result(batch_id)`
6. `explain_quarantined_record(batch_id, transaction_id)`

All six tools read only from persisted `raw`, `processed`, `quarantine` and `audit` surfaces.
There is no write/update/delete tool, arbitrary SQL access or arbitrary shell execution.

## Decision ownership

The MCP service deliberately does **not** import `DataQualityEngine`, `GoldenPathPipeline` or the
reconciliation engine. It reads the evidence produced by those existing Python components.
Therefore:

- Python deterministic domain engine decides DQ and reconciliation.
- MCP tools expose evidence.
- The assistant explains evidence.
- AI does not make or override finance decisions.

## Controlled AI operations adapter

`ControlledOperationsAssistant` is deterministic and API-key free. It supports the frozen candidate
questions:

- `Why was this batch initially blocked?`
- `Is this batch safe for analytics?`
- `What happened to transaction TX-01011?`

Each response includes `evidence_used` plus the structured tool outputs. Unknown prompts fail closed;
there is intentionally no live-LLM fallback in the golden path.

## MCP transport

The primary integration is `finbridge_mcp.sdk_server`, built on the **official MCP Python SDK v2**
(`MCPServer`) with `read_only_hint=True` and `open_world_hint=False` on all six tools. CI installs
`mcp>=2,<3` and validates list/call behavior through the SDK client.

`python -m finbridge_mcp` also provides a tiny dependency-free stdio JSON-RPC harness for offline
contract smoke tests when the SDK package cannot be installed. It is a test harness, not the primary
production protocol implementation.

## Safety thesis

`AI explanation != finance decision`

This is the PASS 5 recruitment signal: operational AI receives controlled read-only evidence instead
of unrestricted database/shell access, while deterministic Python rules remain authoritative.
