#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_TOOLS = [
    "get_batch_status",
    "get_data_quality_summary",
    "list_batch_anomalies",
    "trace_transaction",
    "get_reconciliation_result",
    "explain_quarantined_record",
]


def main() -> None:
    required = [
        "scripts/pass8_gate.sh",
        "scripts/pass8_golden_regression.py",
        "scripts/pass8_security_scan.py",
        ".github/workflows/pass8-production-hardening.yml",
        "requirements-pass8.txt",
        "PASS8_EVIDENCE.md",
        "PASS8_REVIEW_GATE.md",
    ]
    missing = [item for item in required if not (ROOT / item).exists()]
    if missing:
        raise AssertionError(f"PASS 8 artifacts missing: {missing}")

    if (ROOT / "contracts/current_pass.txt").read_text(encoding="utf-8").strip() != "8":
        raise AssertionError("Current pass marker must be 8")

    versions = (ROOT / "infra/terraform/versions.tf").read_text(encoding="utf-8")
    if 'required_version = "~> 1.16.0"' not in versions or 'version = "4.81.0"' not in versions:
        raise AssertionError("Terraform/Terraform AzureRM pin changed")

    pass6_hashes = {
        "infra/terraform/main.tf": "0a22d48822ce69efa25fabadde4ff1205ee851a22e6c514c8f21b30bb59cf3d3",
        "infra/terraform/providers.tf": "86f53e037a5b8c98f06133e05ce13f7f213f451d1c529e08780ef875abcd012f",
        "infra/terraform/variables.tf": "a8bb84bdd1d8fb1484a1ec77506811b6dad3e4fc865b9147b03408de28ca9444",
        "infra/terraform/outputs.tf": "d613aaeca3db0cf7261ed733535a4e349070845459ddce46c7ee7c7ae4f1554c",
        "infra/terraform/versions.tf": "1ecda10a19ce238d7d2f000591ff6ee04549aae3e3905dcde41491620f21af5d",
        "infra/terraform/terraform.tfvars.example": "61a0c818f0066a3614ec9cb9b99d15d6ad9377bf3f6cfe32704cd65f2dd23a5b",
    }
    for relative, expected_hash in pass6_hashes.items():
        actual_hash = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise AssertionError(f"PASS 6 Terraform source continuity changed: {relative}")

    sdk = (ROOT / "services/mcp/finbridge_mcp/sdk_server.py").read_text(encoding="utf-8")
    names = re.findall(r"^\s*def ([a-z_]+)\(", sdk, flags=re.MULTILINE)
    exposed = [name for name in names if name in EXPECTED_TOOLS]
    if exposed != EXPECTED_TOOLS:
        raise AssertionError(f"Official MCP adapter tool set/order changed: {exposed}")
    if "read_only_hint=True" not in sdk or "open_world_hint=False" not in sdk:
        raise AssertionError("MCP annotations are not explicitly read-only/closed-world")

    combined_mcp = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "services/mcp/finbridge_mcp").glob("*.py")
    ).lower()
    for forbidden in ("run_sql", "execute_shell", "delete_batch", "update_batch", "write_record"):
        if f'"{forbidden}"' in combined_mcp or f"'{forbidden}'" in combined_mcp:
            raise AssertionError(f"Forbidden MCP surface found: {forbidden}")

    layout = (ROOT / "apps/demo-web/app/layout.tsx").read_text(encoding="utf-8")
    evidence = (ROOT / "apps/demo-web/data/candidate-evidence.ts").read_text(encoding="utf-8")
    if "robots: { index: false, follow: false }" not in layout:
        raise AssertionError("Frontend noindex/nofollow metadata missing")
    if "AlpineBank is fictional" not in evidence or "No uCloudify client data" not in evidence:
        raise AssertionError("Synthetic/non-internal disclaimer changed")
    for route in ("app/page.tsx", "app/quality/page.tsx", "app/operations/page.tsx", "app/architecture/page.tsx", "app/candidate/page.tsx"):
        if not (ROOT / "apps/demo-web" / route).exists():
            raise AssertionError(f"Candidate route missing: {route}")

    golden = json.loads((ROOT / "apps/demo-web/data/golden-path.json").read_text(encoding="utf-8"))
    ready = next(stage for stage in golden["stages"] if stage["state"] == "READY_FOR_ANALYTICS")
    if ready["reconciliation"]["difference_eur"] != "0.00" or ready["unaccounted_records"] != 0:
        raise AssertionError("Frozen reconciliation/accountability evidence changed")

    workflow = (ROOT / ".github/workflows/pass8-production-hardening.yml").read_text(encoding="utf-8").lower()
    if "terraform apply" in workflow or "deploy" in workflow:
        raise AssertionError("PASS 8 CI must not deploy or run terraform apply")

    print("PASS 8 STRUCTURAL HARDENING VALIDATION: GREEN")
    print("PASS: frozen Terraform provider pin and all six PASS 6 source hashes preserved")
    print("PASS: exactly six read-only/closed-world MCP tools preserved")
    print("PASS: five candidate routes + noindex + synthetic disclaimer preserved")
    print("PASS: CI contains no deploy or terraform apply step")


if __name__ == "__main__":
    main()
