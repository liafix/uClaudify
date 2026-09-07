# FinBridge Cloud — PASS 2 Evidence

## Scope

PASS 2 implements **Finance Domain Engine + Data Quality Hardening** only. It closes the frozen
`DQ-01..DQ-05` and `FIN-01..FIN-05` contracts with executable tests while preserving the PASS 1
golden candidate-demo story.

## Implementation evidence

- Added an explicit `RawTransactionRecord` trust boundary so malformed runtime values can be tested
  before promotion to canonical `Transaction`.
- Added `DataQualityEngine` for DQ-01 through DQ-04.
- DQ-03 normalizes exact monetary strings to `Decimal` and rejects invalid/non-finite/binary-float
  monetary inputs at the trust boundary.
- Added immutable `InMemoryBatchLedger` for DQ-05 / FIN-05 replay semantics.
- Exact replay creates zero new import effects and keeps one committed dataset.
- Same batch id with changed source payload fails closed.
- Same batch id/source payload with changed accepted/quarantine decision counts also fails closed.
- Added reusable FIN-01..FIN-04 invariant functions independent from UI/cloud code.
- `GoldenPathPipeline` now delegates validation/reconciliation/replay evidence to those hardened
  components instead of embedding the rules inline or hardcoding replay success.

## Executable contract matrix

| Contract | PASS 2 evidence |
|---|---|
| DQ-01 | Duplicate transaction id produces `DUPLICATE_TRANSACTION` and only one row is accepted. |
| DQ-02 | Unsupported currency produces `INVALID_CURRENCY:*`. |
| DQ-03 | Invalid/non-finite/float amount is rejected; exact decimal string becomes `Decimal`. |
| DQ-04 | Every frozen required field is independently tested fail-closed. |
| DQ-05 | Exact retry has 0 new accepted / 0 duplicate imports / 0 additional quarantine; changed replay fails closed. |
| FIN-01 | Duplicate accepted source-line identity is rejected. |
| FIN-02 | Duplicate transaction id cannot exist in verified output. |
| FIN-03 | Accepted/quarantined sets must be disjoint and exactly partition source rows. |
| FIN-04 | Reconciliation is recomputed only from accepted records; tampered totals fail. |
| FIN-05 | Replays preserve exactly one committed dataset. |

## Local validation

Environment used for the final local gate:

- Python `3.13.5` (project contract remains `>=3.12`)
- OpenJDK `21.0.11`
- Node `22.16.0`
- npm `10.9.2`
- TypeScript `5.8.3`

`./scripts/pass2_gate.sh` result: **GREEN**.

Python suite result: **27/27 PASS**.

The gate also re-runs:

- PASS 0 frozen contract / scope / secret-hygiene checks,
- PASS 1 executable golden-path regression validation,
- frontend evidence vs Python source-of-truth contract check,
- Java legacy-boundary compile/smoke,
- TypeScript fallback declaration check,
- Python bytecode compilation.

## PASS 1 recruitment evidence preserved

The hardened engine still produces exactly:

- 1,024 input records,
- 1,019 accepted,
- 3 duplicate anomalies,
- 2 invalid-currency anomalies,
- 5 quarantined,
- 0 unaccounted,
- €125,400.00 accepted credits,
- €98,700.00 accepted debits,
- €1,026,700.00 calculated closing balance,
- €0.00 reconciliation difference,
- exact replay with zero new import effects,
- final `READY_FOR_ANALYTICS`.

The committed frontend evidence remains generated from the Python domain engine.

## Honest pending evidence

The sandbox still does not contain installed Next.js dependencies, so PASS 2 does **not** claim a
fresh local `next build`. The GitHub Actions PASS 2 workflow installs frontend dependencies and runs
the production build. Closing the full CI/build/security release gate remains a later hardening pass
as planned.

Azure/Azurite persistence, real Java export mapping, MCP, and Terraform resource implementation are
explicitly not part of PASS 2.
