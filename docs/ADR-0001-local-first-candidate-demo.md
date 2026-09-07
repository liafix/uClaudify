# ADR-0001 — Local-first candidate demo

**Status:** Accepted in PASS 0

## Decision

The golden path must run deterministically without Azure or LLM credentials. Cloud and AI integrations extend the proof later but cannot become a prerequisite for reviewing the candidate demo.

## Why

A recruitment artifact should remain inspectable, reproducible and inexpensive. This also separates domain correctness from infrastructure availability.
