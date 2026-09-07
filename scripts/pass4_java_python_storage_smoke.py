#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for relative in ("services/domain", "services/storage", "services/processing"):
    sys.path.insert(0, str(ROOT / relative))

from finbridge_domain.golden_path import run_golden_path  # noqa: E402
from finbridge_processing import ProcessingOrchestrator, load_canonical_csv  # noqa: E402
from finbridge_storage import build_in_memory_storage  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: pass4_java_python_storage_smoke.py <java-canonical.csv>")
    batch = load_canonical_csv(sys.argv[1])
    runtime = ProcessingOrchestrator(build_in_memory_storage()).run_golden_path(batch)
    if runtime != run_golden_path():
        raise AssertionError("Java -> Python -> storage evidence diverged from frozen golden path")
    print("PASS 4 Java -> Python -> storage golden path: PASS")


if __name__ == "__main__":
    main()
