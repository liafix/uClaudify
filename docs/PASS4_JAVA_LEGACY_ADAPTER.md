# PASS 4 — Java legacy adapter end-to-end

## Goal

Turn the previously skeletal Java boundary into an executable compatibility adapter without moving any finance-domain authority out of Python.

## Flow

`LegacyTransaction (Java) -> LegacyTransactionMapper -> CanonicalTransaction -> canonical CSV -> Python legacy_import -> existing ProcessingOrchestrator -> existing storage/Azurite golden path`

## Ownership boundary

### Java owns

- the fictional AlpineBank legacy transaction shape,
- deterministic synthetic legacy-source generation,
- structural movement-code conversion from `CR`/`DR` to canonical `CREDIT`/`DEBIT`,
- canonical transport mapping/export.

### Python owns

- DQ-01 duplicate detection,
- DQ-02 currency validation,
- DQ-03/DQ-04 validation,
- quarantine decisions,
- FIN-01..FIN-05,
- financial reconciliation,
- persisted idempotency,
- `READY_FOR_ANALYTICS`.

The Java exporter deliberately emits the three repeated transaction IDs and the invalid `EUX` / `EURO` currencies unchanged. This makes the language boundary observable while preventing Java from becoming a second domain engine.

## Evidence contract

The Java-origin canonical batch must be byte-semantically equivalent to the frozen Python fixture after CSV parsing, including source-line derivation. Running it through the existing Python orchestration path must preserve the exact candidate evidence:

- 1,024 input,
- 1,019 accepted,
- 5 quarantined,
- €0.00 reconciliation difference,
- replay creates no second dataset,
- final state `READY_FOR_ANALYTICS`.

A separate real-Azurite smoke script performs the same check against the Azure Blob adapter.
