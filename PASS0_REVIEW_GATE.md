# FinBridge Cloud — PASS 0 Review Gate

Status is generated/confirmed by running `./scripts/pass0_gate.sh`.

## Scope delivered

- repository foundation,
- machine-readable frozen candidate/demo contract,
- Python domain contract + unit tests,
- Java legacy-boundary contract + executable smoke test,
- Next.js-oriented candidate shell + TypeScript/contract checks,
- Terraform Azure-provider/naming foundation,
- CI skeleton for contract + Terraform validation,
- explicit non-goals and synthetic-data disclaimer,
- secret-hygiene and later-pass-isolation checks.

## Frozen facts

- 1,024 synthetic input records
- 1,019 accepted
- 3 duplicates
- 2 invalid currency records
- 5 quarantined
- 0 unaccounted
- expected closing balance EUR 1,026,700.00
- first quality decision must be `QUALITY_BLOCKED`
- final golden state is `READY_FOR_ANALYTICS`

## Not implemented yet

No ingestion engine, generated 1,024-row fixture, quarantine behavior, reconciliation engine, replay/idempotency runtime, Azure Function, MCP server, AI explanation, live deployment or final candidate UX exists in PASS 0.

## Review decision

Do not begin PASS 1 until this gate is explicitly approved.
