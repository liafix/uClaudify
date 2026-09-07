#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "README.md",
    "contracts/pass0_contract.json",
    "fixtures/alpinebank/batch_manifest.json",
    "services/domain/finbridge_domain/contracts.py",
    "adapters/legacy-java/src/main/java/com/finbridge/legacy/CanonicalContract.java",
    "apps/demo-web/app/page.tsx",
    "infra/terraform/versions.tf",
    "docs/FROZEN_DOMAIN_CONTRACT.md",
    ".github/workflows/pass0.yml",
)

SECRET_PATTERNS = {
    "OpenAI-style API key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Stripe secret": re.compile(r"\bsk_(?:live|test)_[A-Za-z0-9]{10,}\b"),
    "Stripe webhook secret": re.compile(r"\bwhsec_[A-Za-z0-9]{10,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate_structure() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f"Missing PASS 0 paths: {missing}")


def validate_scenario() -> None:
    contract = load_json("contracts/pass0_contract.json")
    fixture = load_json("fixtures/alpinebank/batch_manifest.json")
    s = contract["scenario"]
    r = fixture["records"]
    c = fixture["control_totals"]

    expected = {
        "input_records": 1024,
        "accepted_records": 1019,
        "duplicate_records": 3,
        "invalid_currency_records": 2,
        "quarantined_records": 5,
        "unaccounted_records": 0,
    }
    for key, value in expected.items():
        if s[key] != value:
            raise AssertionError(f"Frozen scenario mismatch for {key}: {s[key]} != {value}")

    if r["input"] != r["accepted"] + r["quarantined"] + r["unaccounted"]:
        raise AssertionError("Fixture record accountability is not exact")
    if r["quarantined"] != r["duplicates"] + r["invalid_currency"]:
        raise AssertionError("Quarantine count does not equal frozen anomaly counts")

    calculated = Decimal(c["opening_balance"]) + Decimal(c["credits"]) - Decimal(c["debits"])
    if calculated != Decimal(c["expected_closing_balance"]):
        raise AssertionError("Financial control totals do not reconcile")

    golden = contract["golden_states"]
    if golden[4] != "QUALITY_BLOCKED" or golden[-1] != "READY_FOR_ANALYTICS":
        raise AssertionError("Golden-path state contract changed")

    if not contract["synthetic_only"]:
        raise AssertionError("Candidate demo must remain synthetic-only")


def validate_scope_contract() -> None:
    contract = load_json("contracts/pass0_contract.json")
    prohibited = set(contract["prohibited_scope"])
    required_prohibited = {
        "real bank/customer data",
        "uCloudify proprietary data or code",
        "authentication/user management",
        "live LLM dependency for the golden path",
        "arbitrary SQL tool access",
        "arbitrary shell execution from AI",
    }
    if not required_prohibited.issubset(prohibited):
        raise AssertionError("PASS 0 prohibited scope weakened")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "AlpineBank is fictional" not in readme:
        raise AssertionError("Candidate disclaimer is not visible in README")


def validate_secret_hygiene() -> None:
    text_extensions = {".md", ".py", ".java", ".json", ".tf", ".tsx", ".ts", ".mjs", ".yml", ".yaml", ".example"}
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix not in text_extensions and path.name != ".env.example":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{label}: {path.relative_to(ROOT)}")
    if findings:
        raise AssertionError(f"Secret-like material found: {findings}")


def validate_no_accidental_implementation() -> None:
    # PASS 0 must not pretend that later features are already implemented.
    forbidden_paths = (
        "services/mcp",
        "services/reconciliation",
        "functions/azure",
        "apps/demo-web/app/operations",
    )
    current_pass_file = ROOT / "contracts" / "current_pass.txt"
    current_pass = int(current_pass_file.read_text(encoding="utf-8").strip()) if current_pass_file.exists() else 0
    existing = [path for path in forbidden_paths if (ROOT / path).exists()]
    if current_pass <= 0 and existing:
        raise AssertionError(f"Later-pass implementation leaked into PASS 0: {existing}")


def main() -> None:
    checks = [
        ("repository structure", validate_structure),
        ("frozen scenario", validate_scenario),
        ("scope contract", validate_scope_contract),
        ("secret hygiene", validate_secret_hygiene),
        ("pass isolation", validate_no_accidental_implementation),
    ]
    for label, fn in checks:
        fn()
        print(f"PASS: {label}")
    print("PASS 0 structural/domain validation: PASS")


if __name__ == "__main__":
    main()
