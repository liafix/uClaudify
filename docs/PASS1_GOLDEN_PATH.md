# PASS 1 — Golden Vertical Slice

PASS 1 proves the complete candidate-demo story locally before cloud/storage/AI expansion.

## Executable state path

```text
RECEIVED
  -> INGESTION_PASS
  -> SCHEMA_PASS
  -> NORMALIZATION_PASS
  -> QUALITY_BLOCKED
  -> QUARANTINED
  -> RECONCILED
  -> IDEMPOTENCY_PASS
  -> READY_FOR_ANALYTICS
```

The interactive frontend compresses the three internal processing states into the single operator action **Process Daily Batch**, while still displaying the complete state history as evidence.

## Frozen failure evidence

At `QUALITY_BLOCKED`:

- input: 1,024
- accepted candidates: 1,019
- detected anomalies: 5
- unresolved/unaccounted: 0
- explicit anomalies:
  - `TX-00482` — `DQ-01` — duplicate transaction
  - `TX-00791` — `DQ-01` — duplicate transaction
  - `TX-00902` — `DQ-01` — duplicate transaction
  - `TX-01011` — `DQ-02` — invalid currency `EUX`
  - `TX-01012` — `DQ-02` — invalid currency `EURO`

The batch is blocked even though ingestion/schema/normalization completed. This is the candidate-demo thesis: **pipeline execution is not the same thing as trustworthy financial data**.

## Quarantine and accountability

After the operator explicitly quarantines the five anomalies:

- accepted: 1,019
- quarantined: 5
- unaccounted: 0
- record accountability: 100%

No bad record is silently dropped.

## Reconciliation

The reconciliation engine uses `Decimal` and only accepted records:

- opening balance: €1,000,000.00
- credits: €125,400.00
- debits: €98,700.00
- expected closing: €1,026,700.00
- calculated closing: €1,026,700.00
- difference: €0.00

## Idempotent replay

Replaying the same frozen batch after reconciliation returns a no-op evidence result:

- new accepted records: 0
- duplicate imports: 0
- additional quarantine rows: 0

Only after reconciliation and replay evidence are clean can the state advance to `READY_FOR_ANALYTICS`.

## Presentation/source-of-truth boundary

The browser does not re-implement the finance decision logic. The Python domain engine is executed by `scripts/export_pass1_demo.py`, and its serialized evidence is committed to `apps/demo-web/data/golden-path.json`. The Next.js shell only presents and steps through that validated evidence.
