# FinBridge Cloud — PASS 5 Evidence

Date: 2026-09-06
Scope: read-only MCP operations server + controlled AI operations evidence. PASS 6 is not implemented.

## PASS 5 implementation

PASS 5 adds exactly six read-only operations tools over the persisted evidence created by the
existing Java -> Python -> storage golden path:

1. `get_batch_status`
2. `get_data_quality_summary`
3. `list_batch_anomalies`
4. `trace_transaction`
5. `get_reconciliation_result`
6. `explain_quarantined_record`

The operations package reads only from the existing `raw`, `processed`, `quarantine` and `audit`
storage surfaces. It deliberately does not import the Python `DataQualityEngine`,
`GoldenPathPipeline` or reconciliation engine, so PASS 5 cannot become a second finance decision
owner.

## Read-only / fail-closed evidence

Executable tests prove that invoking all six tools leaves raw, processed, quarantine, audit events,
commit evidence and commit count unchanged. Unknown tools such as a mutation request fail closed and
are not listed by the MCP server.

No arbitrary SQL, arbitrary shell, write/update/delete batch or finance-decision tool is exposed.

## MCP server evidence

Two transport layers are included:

- `finbridge_mcp.sdk_server` — primary adapter for the official MCP Python SDK v2 using `MCPServer`.
  Every tool is annotated `read_only_hint=True` and `open_world_hint=False`.
- `python -m finbridge_mcp` — dependency-free stdio JSON-RPC compatibility harness for offline
  candidate-demo validation when the package registry is unavailable.

The local stdio smoke executed a real process and verified initialize/notification flow,
`tools/list`, `tools/call`, six-tool discovery and frozen data-quality evidence.

The official SDK adapter is included together with a dedicated executable smoke script and GitHub
Actions job. The local sandbox still cannot resolve the external package registry, but the previously
pending SDK runtime gate was executed in a network-enabled Render environment against `mcp==2.1.1`.
The official `Client(server)` path discovered exactly the six frozen tools, called all six successfully,
and verified `readOnlyHint=true` plus `openWorldHint=false` for every tool.

Network runtime evidence:

- service: `srv-daelkv1t0dsc73aocndg` (`finbridge-pass5-project-smoke-mcp-v2`)
- deploy: `dep-daelkvpt0dsc73aocpmg`
- deploy status: `LIVE`
- MCP package: `2.1.1`
- exact project `sdk_server.py` SHA-256: `5d2963b5d09d968978c9f6f28aa0540c6ab8d3e1b6ac2fb96a16093144d75c7b`
- exact project `pass5_official_sdk_smoke.py` SHA-256: `1c96af642425e582cd1fee1fa1665d17165f659661e474d413edc81d6053937a`
- source-hash verification before execution: PASS
- `tools/list`: 6/6 exact tools PASS
- `tools/call`: 6/6 PASS
- read-only annotations: 6/6 PASS
- closed-world annotations: 6/6 PASS

The network runner executed the exact synchronized project SDK adapter and exact six-tool smoke script
(hash-verified before execution) against the official `mcp==2.1.1` package. To keep this gate focused
on external SDK compatibility, the remote runtime supplied deterministic frozen operation responses
with the same shapes and candidate evidence. The actual FinBridge OperationsService semantics and
persisted-evidence immutability remain independently proven by the project's 16/16 executable MCP
tests and dependency-free stdio process smoke. Together the gates prove actual tool behavior plus
official MCP SDK v2 wiring/client compatibility.

## Official MCP SDK v2 runtime gate

The external-package runtime blocker is closed. Network-enabled Render validation installed
`mcp==2.1.1`, verified SHA-256 for the exact project `sdk_server.py` and synchronized
`scripts/pass5_official_sdk_smoke.py`, then executed that smoke through the official MCP v2
`Client(server)` interface. All six tools were listed and called; every tool advertised
`readOnlyHint=true` and `openWorldHint=false`. The frozen candidate evidence remained
`1,024 -> 1,019 + 5 quarantine -> EUR 0.00 -> READY_FOR_ANALYTICS`.

The remote gate used a deterministic frozen operation provider to isolate SDK/client wiring. Actual
FinBridge persisted-evidence behavior is separately covered by the local executable MCP suite and
stdio server smoke.

## Controlled AI operations evidence

The golden path has no live LLM dependency. `ControlledOperationsAssistant` only supports frozen,
reviewable candidate-demo questions and fails closed for arbitrary prompts. Every response includes
`evidence_used` and the structured outputs that support the explanation.

Frozen example:

- Question: `Why was this batch initially blocked?`
- Evidence tools: `get_data_quality_summary`, `list_batch_anomalies`,
  `get_reconciliation_result`
- Answer facts: 3 duplicate records, 2 invalid-currency records, 1,019 accepted, 5 quarantined,
  reconciliation difference EUR 0.00.

The assistant explicitly states that the deterministic Python pipeline, not AI, owns DQ,
reconciliation and readiness decisions.

Machine-readable evidence: `artifacts/pass5/ai-operations-evidence.json`.

## Regression results

PASS 0..4 structural and domain regressions remain green.

Python suites:

- domain: 27/27 PASS
- storage: 3/3 PASS
- processing: 6/6 PASS
- PASS 5 MCP/assistant/read-only: 16/16 PASS
- total Python tests: **52/52 PASS**

Additional gates:

- Java PASS 0 + PASS 4 adapter/export + Java -> Python -> storage: PASS
- frontend evidence contract: PASS via documented fallback because npm dependencies are absent in
  this sandbox
- MCP stdio process smoke: PASS
- Python compileall across domain/storage/processing/MCP/functions: PASS
- PASS 5 structural/safety validator: PASS

Full evidence log: `PASS5_LOCAL_REGRESSION_2026-09-06.log`.
Post-SDK-sync verification log: `PASS5_POST_SDK_SYNC_VERIFICATION_2026-09-06.log` (PASS5 validator, 16/16 MCP tests, stdio process smoke, smoke-script compile, PASS 6 isolation).

## Frozen candidate story remains unchanged

The MCP/AI observation layer does not alter the underlying proof:

`1,024 input -> 1,019 accepted + 5 quarantined -> EUR 0.00 reconciliation -> idempotent replay -> READY_FOR_ANALYTICS`

PASS 4 real Java -> Python -> Azurite evidence remains inherited and unchanged.

## PASS 5 scope isolation

Not implemented in PASS 5:

- Terraform production Azure hardening (PASS 6)
- candidate UX/presentation hardening
- live LLM dependency
- authentication
- real bank/customer data
- arbitrary SQL/shell access

