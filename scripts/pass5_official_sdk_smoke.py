#!/usr/bin/env python3
"""Validate all six FinBridge tools through the official MCP Python SDK v2 client."""
from __future__ import annotations

import asyncio

from mcp import Client

from finbridge_mcp.sdk_server import build_mcp_server


BATCH_ID = "2026-09-05-001"
EXPECTED_TOOLS = [
    "get_batch_status",
    "get_data_quality_summary",
    "list_batch_anomalies",
    "trace_transaction",
    "get_reconciliation_result",
    "explain_quarantined_record",
]


def _structured(result: object) -> dict[str, object]:
    data = getattr(result, "structured_content", None)
    if data is None:
        data = getattr(result, "structuredContent", None)
    if not isinstance(data, dict):
        raise AssertionError(f"Official SDK tool result did not expose structured content: {result!r}")
    return data


def _annotation_value(annotations: object, snake: str, camel: str) -> object:
    value = getattr(annotations, snake, None)
    if value is None:
        value = getattr(annotations, camel, None)
    return value


async def run() -> None:
    server = build_mcp_server()
    async with Client(server) as client:
        listed = await client.list_tools()
        names = [tool.name for tool in listed.tools]
        if names != EXPECTED_TOOLS:
            raise AssertionError(f"Official MCP SDK tool list diverged: {names}")

        for tool in listed.tools:
            if tool.annotations is None:
                raise AssertionError(f"Missing tool annotations: {tool.name}")
            if _annotation_value(tool.annotations, "read_only_hint", "readOnlyHint") is not True:
                raise AssertionError(f"Tool is not read-only: {tool.name}")
            if _annotation_value(tool.annotations, "open_world_hint", "openWorldHint") is not False:
                raise AssertionError(f"Tool is not closed-world: {tool.name}")

        status = _structured(
            await client.call_tool("get_batch_status", {"batch_id": BATCH_ID})
        )
        quality = _structured(
            await client.call_tool("get_data_quality_summary", {"batch_id": BATCH_ID})
        )
        anomalies = _structured(
            await client.call_tool("list_batch_anomalies", {"batch_id": BATCH_ID})
        )
        trace = _structured(
            await client.call_tool(
                "trace_transaction",
                {"batch_id": BATCH_ID, "transaction_id": "TX-01011"},
            )
        )
        recon = _structured(
            await client.call_tool("get_reconciliation_result", {"batch_id": BATCH_ID})
        )
        explanation = _structured(
            await client.call_tool(
                "explain_quarantined_record",
                {"batch_id": BATCH_ID, "transaction_id": "TX-01011"},
            )
        )

        if status["current_state"] != "READY_FOR_ANALYTICS":
            raise AssertionError("Official SDK batch-status evidence diverged")
        if status["committed_dataset_count"] != 1:
            raise AssertionError("Official SDK commit-count evidence diverged")

        if quality["input_records"] != 1024 or quality["accepted_records"] != 1019:
            raise AssertionError("Official SDK quality-count evidence diverged")
        if quality["quarantined_records"] != 5 or quality["unaccounted_records"] != 0:
            raise AssertionError("Official SDK quarantine/accountability evidence diverged")
        if quality["issues_by_rule"] != {"DQ-01": 3, "DQ-02": 2}:
            raise AssertionError("Official SDK DQ-rule evidence diverged")

        if anomalies["count"] != 5 or len(anomalies["anomalies"]) != 5:
            raise AssertionError("Official SDK anomaly-list evidence diverged")

        if trace["outcome"] != "QUARANTINED":
            raise AssertionError("Official SDK trace outcome diverged")
        if len(trace["raw_occurrences"]) != 1 or len(trace["accepted_occurrences"]) != 0:
            raise AssertionError("Official SDK trace occurrence evidence diverged")
        if len(trace["quarantined_occurrences"]) != 1:
            raise AssertionError("Official SDK quarantine trace evidence diverged")

        if recon["difference_eur"] != "0.00" or recon["reconciled"] is not True:
            raise AssertionError("Official SDK reconciliation evidence diverged")

        if explanation["decision_owner"] != "Python deterministic data-quality engine":
            raise AssertionError("Official SDK decision-owner evidence diverged")
        if explanation["ai_decision"] is not False:
            raise AssertionError("Official SDK AI-decision boundary diverged")
        details = explanation["explanation"]
        if not isinstance(details, list) or len(details) != 1:
            raise AssertionError("Official SDK quarantine explanation diverged")
        if details[0]["rule"] != "DQ-02" or details[0]["reason"] != "INVALID_CURRENCY:EUX":
            raise AssertionError("Official SDK quarantine rule evidence diverged")

    print("PASS 5 official MCP Python SDK v2 six-tool list/call/readOnlyHint smoke: PASS")


if __name__ == "__main__":
    asyncio.run(run())
