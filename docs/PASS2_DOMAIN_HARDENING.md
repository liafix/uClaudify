# PASS 2 — Finance Domain Engine + Data Quality Hardening

PASS 2 turns the PASS 1 recruitment story into explicit executable finance/data contracts without
adding Azure, storage persistence, MCP, or a production Java exporter.

## DQ contract

| Rule | Executable enforcement |
|---|---|
| DQ-01 | `DataQualityEngine` keeps one accepted row per `transaction_id`; later occurrences are blocking anomalies. |
| DQ-02 | Currency must be in the frozen allowed set (`EUR`, `USD`, `GBP`, `CHF`). |
| DQ-03 | Untrusted amount must normalize to a finite exact `Decimal`; binary floats are rejected at the trust boundary. |
| DQ-04 | Every required canonical string field must be non-empty before normalization. |
| DQ-05 | `InMemoryBatchLedger` proves exact replay creates zero new accepted/quarantine effects and a changed payload under the same batch id fails closed. |

## Finance invariant contract

| Invariant | Executable enforcement |
|---|---|
| FIN-01 | Accepted source rows are unique by source-line identity, so one accepted row cannot be counted twice. |
| FIN-02 | Verified output contains unique transaction ids. |
| FIN-03 | Accepted and quarantined source-line sets are disjoint and exactly partition the input set. |
| FIN-04 | Reconciliation is recomputed strictly from accepted records; quarantined records cannot affect totals. |
| FIN-05 | One batch id maps to exactly one immutable committed dataset across exact replays. |

## Trust boundary

`RawTransactionRecord` intentionally accepts untrusted runtime values. Only `DataQualityEngine` may
promote a raw record to canonical `Transaction`. This makes DQ-03 and DQ-04 real runtime properties
rather than assumptions hidden behind Python type annotations.

## Replay semantics

The PASS 2 ledger is in-memory by design. It establishes the semantics that PASS 3 storage adapters
must preserve:

1. the first reconciled batch is committed once,
2. an exact retry returns zero new import effects,
3. a known batch id with changed source content fails closed,
4. the dataset cardinality remains exactly one.

## Scope held back deliberately

- no Azure Blob/Azurite persistence yet (PASS 3),
- no real Java mapping/export adapter yet (PASS 4),
- no MCP operations server yet (PASS 5),
- no Terraform resource hardening yet (PASS 6).
