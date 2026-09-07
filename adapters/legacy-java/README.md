# Legacy Java adapter — PASS 4

This module is the explicit compatibility boundary for the fictional AlpineBank legacy source.

PASS 4 proves that Java can represent the legacy transaction model, map the legacy `CR` / `DR`
movement codes to the frozen canonical transport contract, and export a deterministic 1,024-row CSV
that the Python processing boundary consumes directly.

Java intentionally does **not** own duplicate detection, currency validation, quarantine,
reconciliation, idempotency or analytics-readiness decisions. Those remain in the Python domain
engine.
