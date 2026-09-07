#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "domain"))

from finbridge_domain.golden_path import run_golden_path  # noqa: E402

OUTPUT = ROOT / "apps" / "demo-web" / "data" / "golden-path.json"


def main() -> None:
    payload = run_golden_path()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + os.linesep, encoding="utf-8")
    print(f"PASS 1 demo evidence exported: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
