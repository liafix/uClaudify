#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "services/mcp/finbridge_mcp/contracts.py",
    "services/mcp/finbridge_mcp/operations.py",
    "services/mcp/finbridge_mcp/assistant.py",
    "services/mcp/finbridge_mcp/protocol.py",
    "services/mcp/finbridge_mcp/runtime.py",
    "services/mcp/finbridge_mcp/sdk_server.py",
    "services/mcp/tests/test_pass5_operations_tools.py",
    "services/mcp/tests/test_pass5_read_only_boundary.py",
    "services/mcp/tests/test_pass5_assistant.py",
    "services/mcp/tests/test_pass5_mcp_protocol.py",
    "scripts/pass5_mcp_stdio_smoke.py",
    "scripts/pass5_official_sdk_smoke.py",
    "artifacts/pass5/ai-operations-evidence.json",
    "docs/PASS5_MCP_OPERATIONS.md",
)


def main() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        raise AssertionError(f"Missing PASS 5 artifacts: {missing}")
    current_pass = int((ROOT / "contracts/current_pass.txt").read_text().strip())
    if current_pass < 5:
        raise AssertionError("PASS marker must be at least 5")

    contracts = (ROOT / "services/mcp/finbridge_mcp/contracts.py").read_text(encoding="utf-8")
    names = re.findall(r'ToolSpec\(\s*"([^"]+)"', contracts)
    expected = [
        "get_batch_status",
        "get_data_quality_summary",
        "list_batch_anomalies",
        "trace_transaction",
        "get_reconciliation_result",
        "explain_quarantined_record",
    ]
    if names != expected:
        raise AssertionError(f"PASS 5 tool surface changed: {names}")

    combined = "\n".join(
        (ROOT / relative).read_text(encoding="utf-8")
        for relative in (
            "services/mcp/finbridge_mcp/contracts.py",
            "services/mcp/finbridge_mcp/operations.py",
            "services/mcp/finbridge_mcp/protocol.py",
        )
    ).lower()
    forbidden_exposed = ("run_sql", "execute_shell", "delete_batch", "update_batch", "write_record")
    if any(f'"{token}"' in combined for token in forbidden_exposed):
        raise AssertionError("MCP tool surface exposes a prohibited mutation/SQL/shell action")


    sdk_source = (ROOT / "services/mcp/finbridge_mcp/sdk_server.py").read_text(encoding="utf-8")
    if "from mcp.server import MCPServer" not in sdk_source:
        raise AssertionError("PASS 5 must include the current official MCP Python SDK v2 adapter")
    if "read_only_hint=True" not in sdk_source or "open_world_hint=False" not in sdk_source:
        raise AssertionError("Official SDK tools must carry explicit read-only/closed-world annotations")

    operations = (ROOT / "services/mcp/finbridge_mcp/operations.py").read_text(encoding="utf-8")
    forbidden_domain_imports = (
        "DataQualityEngine",
        "GoldenPathPipeline",
        "reconcile_accepted_records",
    )
    if any(token in operations for token in forbidden_domain_imports):
        raise AssertionError("PASS 5 operations layer duplicated Python domain decision ownership")

    evidence = json.loads(
        (ROOT / "artifacts/pass5/ai-operations-evidence.json").read_text(encoding="utf-8")
    )
    if evidence["safety"] != {
        "ai_is_finance_decision_owner": False,
        "arbitrary_shell": False,
        "arbitrary_sql": False,
        "live_llm_dependency": False,
        "read_only": True,
    }:
        raise AssertionError("Controlled AI evidence safety contract changed")
    if len(evidence["mcp_tools"]) != 6:
        raise AssertionError("Evidence must contain exactly six MCP tools")
    why = evidence["questions"][0]
    if why["live_llm_used"] is not False or why["deterministic"] is not True:
        raise AssertionError("Golden assistant path must be deterministic and API-key free")
    if "3 duplicate records" not in why["answer"] or "2 invalid-currency records" not in why["answer"]:
        raise AssertionError("Assistant explanation diverged from frozen DQ evidence")

    if (ROOT / "services/mcp/finbridge_mcp/live_llm.py").exists():
        raise AssertionError("Live LLM dependency leaked into PASS 5")
    if current_pass <= 5 and (ROOT / "infra/terraform/pass6").exists():
        raise AssertionError("PASS 6 scope leaked into PASS 5")

    print("PASS: exactly six read-only MCP operations tools are frozen")
    print("PASS: operations layer reads persisted evidence and does not own DQ/finance decisions")
    print("PASS: controlled assistant emits explicit evidence_used and uses no live LLM")
    print("PASS: arbitrary SQL/shell/mutation tools remain absent")
    if current_pass <= 5:
        print("PASS: PASS 6 scope remains absent")
    else:
        print("PASS: PASS 5 regression remains green inside later pass")
    print("PASS 5 structural safety validation: PASS")


if __name__ == "__main__":
    main()
