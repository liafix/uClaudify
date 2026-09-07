#!/usr/bin/env python3
"""Executable JSON-RPC MCP stdio smoke without external MCP/LLM dependencies."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
env = os.environ.copy()
env["PYTHONPATH"] = ":".join(
    str(ROOT / relative)
    for relative in ("services/domain", "services/storage", "services/processing", "services/mcp")
)
requests = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
    {"jsonrpc": "2.0", "method": "notifications/initialized"},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_data_quality_summary",
            "arguments": {"batch_id": "2026-09-05-001"},
        },
    },
]
proc = subprocess.run(
    [sys.executable, "-m", "finbridge_mcp"],
    input="".join(json.dumps(item) + "\n" for item in requests),
    text=True,
    capture_output=True,
    env=env,
    check=True,
)
responses = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
if len(responses) != 3:
    raise AssertionError(f"Expected 3 MCP responses, got {len(responses)}: {proc.stdout!r}")
if responses[0]["result"]["serverInfo"]["name"] != "finbridge-read-only-operations":
    raise AssertionError("Unexpected MCP server identity")
if len(responses[1]["result"]["tools"]) != 6:
    raise AssertionError("MCP server must expose exactly six tools")
summary = responses[2]["result"]["structuredContent"]
if summary["accepted_records"] != 1019 or summary["quarantined_records"] != 5:
    raise AssertionError("MCP tool evidence diverged from frozen candidate story")
print("PASS 5 MCP stdio JSON-RPC handshake + tools/list + tools/call: PASS")
