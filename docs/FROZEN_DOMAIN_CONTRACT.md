# Frozen Domain Contract — PASS 0

Status: **FROZEN / REVIEW REQUIRED FOR CHANGES**

## Recruitment purpose

FinBridge Cloud exists primarily as an independent candidate demonstration for uCloudify. It must show engineering judgment, not simulate access to uCloudify systems.

## Synthetic scenario

- Client: `AlpineBank` — fictional.
- Batch: `2026-09-05-001`.
- Input: **1,024** records.
- Accepted after quality handling: **1,019**.
- Duplicate records: **3**.
- Invalid currency records: **2**.
- Quarantined: **5**.
- Unaccounted: **0**.
- Record accountability target: **100%**.

Financial control totals:

- Opening balance: EUR 1,000,000.00
- Credits: EUR 125,400.00
- Debits: EUR 98,700.00
- Expected closing: EUR 1,026,700.00

Money values use exact decimal semantics; floating-point monetary arithmetic is not permitted in the domain engine.

## DQ rules

- **DQ-01** transaction ID unique in batch.
- **DQ-02** currency valid.
- **DQ-03** monetary value Decimal-compatible.
- **DQ-04** canonical required fields present.
- **DQ-05** replay of the same batch is idempotent.

## Financial invariants

- **FIN-01** every accepted record is counted exactly once.
- **FIN-02** duplicate input never enters verified output.
- **FIN-03** every input record has accepted/quarantined outcome.
- **FIN-04** reconciliation uses accepted records only.
- **FIN-05** replay creates no second dataset.

## Golden path states

`RECEIVED -> INGESTION_PASS -> SCHEMA_PASS -> NORMALIZATION_PASS -> QUALITY_BLOCKED -> QUARANTINED -> RECONCILED -> IDEMPOTENCY_PASS -> READY_FOR_ANALYTICS`

The first processing attempt **must** reach `QUALITY_BLOCKED`; silently auto-fixing all anomalies would weaken the candidate story and violate the frozen golden path.

## Authority boundaries

- Python domain code owns quality/reconciliation decisions.
- Java owns only the legacy adapter boundary.
- Frontend is presentation, never domain truth.
- Future MCP/AI can explain evidence, never change a quality/reconciliation decision.
- Azure is an execution/storage option, not a dependency of the deterministic local candidate demo.
