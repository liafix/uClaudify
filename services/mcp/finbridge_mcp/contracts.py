"""Frozen PASS 5 MCP tool contracts.

The contracts are intentionally read-only. The AI/operations layer may inspect persisted evidence,
but it cannot mutate finance state, rerun quality decisions, write storage, execute SQL or invoke a
shell. Python domain/storage evidence remains authoritative.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    input_schema: Mapping[str, Any]

    def as_mcp_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": dict(self.input_schema),
        }


_BATCH_ID_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {"batch_id": {"type": "string"}},
    "required": ["batch_id"],
    "additionalProperties": False,
}

TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(
        "get_batch_status",
        "Read persisted state history and final batch status. Does not mutate processing state.",
        _BATCH_ID_SCHEMA,
    ),
    ToolSpec(
        "get_data_quality_summary",
        "Read accepted/anomaly/quarantine/accountability counts from persisted evidence.",
        _BATCH_ID_SCHEMA,
    ),
    ToolSpec(
        "list_batch_anomalies",
        "List persisted quarantine issues for a batch with rule and source-line evidence.",
        _BATCH_ID_SCHEMA,
    ),
    ToolSpec(
        "trace_transaction",
        "Trace all raw/accepted/quarantined occurrences of a transaction id in a persisted batch.",
        {
            "type": "object",
            "properties": {
                "batch_id": {"type": "string"},
                "transaction_id": {"type": "string"},
            },
            "required": ["batch_id", "transaction_id"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        "get_reconciliation_result",
        "Read persisted reconciliation evidence including the exact difference in EUR.",
        _BATCH_ID_SCHEMA,
    ),
    ToolSpec(
        "explain_quarantined_record",
        "Read the deterministic DQ rule/reason and raw record evidence for one quarantined row.",
        {
            "type": "object",
            "properties": {
                "batch_id": {"type": "string"},
                "transaction_id": {"type": "string"},
            },
            "required": ["batch_id", "transaction_id"],
            "additionalProperties": False,
        },
    ),
)

TOOL_BY_NAME = {tool.name: tool for tool in TOOL_SPECS}
