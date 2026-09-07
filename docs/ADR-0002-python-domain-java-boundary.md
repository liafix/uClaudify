# ADR-0002 — Python owns domain; Java owns legacy boundary

**Status:** Accepted in PASS 0

## Decision

Python is the dominant implementation language for pipeline/domain behavior. Java is intentionally constrained to the compatibility adapter for the synthetic legacy system.

## Why

This demonstrates a modernization/data-bridge pattern without creating a multi-language keyword showcase where responsibilities are unclear.
