"""Official MCP Python SDK v2 adapter for the six frozen PASS 5 read-only tools.

This module is optional at local-golden-path time because the sandbox may not have the `mcp`
package installed. In CI/normal development install `mcp>=2,<3`; the current MCPServer adapter then
exposes the exact same OperationsService semantics validated by the dependency-free core tests.
"""

from __future__ import annotations

from typing import Any

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from .operations import OperationsService
from .runtime import build_seeded_operations_service


READ_ONLY_ANNOTATIONS = ToolAnnotations(read_only_hint=True, open_world_hint=False)


def build_mcp_server(operations: OperationsService | None = None) -> MCPServer:
    ops = operations or build_seeded_operations_service()
    server = MCPServer("FinBridge Read-Only Operations")

    @server.tool(annotations=READ_ONLY_ANNOTATIONS)
    def get_batch_status(batch_id: str) -> dict[str, Any]:
        """Read persisted state history and final batch status."""
        return ops.get_batch_status(batch_id)

    @server.tool(annotations=READ_ONLY_ANNOTATIONS)
    def get_data_quality_summary(batch_id: str) -> dict[str, Any]:
        """Read accepted/anomaly/quarantine/accountability counts."""
        return ops.get_data_quality_summary(batch_id)

    @server.tool(annotations=READ_ONLY_ANNOTATIONS)
    def list_batch_anomalies(batch_id: str) -> dict[str, Any]:
        """List persisted quarantine issues with source-record evidence."""
        return ops.list_batch_anomalies(batch_id)

    @server.tool(annotations=READ_ONLY_ANNOTATIONS)
    def trace_transaction(batch_id: str, transaction_id: str) -> dict[str, Any]:
        """Trace raw, accepted and quarantined occurrences of a transaction."""
        return ops.trace_transaction(batch_id, transaction_id)

    @server.tool(annotations=READ_ONLY_ANNOTATIONS)
    def get_reconciliation_result(batch_id: str) -> dict[str, Any]:
        """Read exact persisted reconciliation evidence."""
        return ops.get_reconciliation_result(batch_id)

    @server.tool(annotations=READ_ONLY_ANNOTATIONS)
    def explain_quarantined_record(batch_id: str, transaction_id: str) -> dict[str, Any]:
        """Read the deterministic DQ rule/reason for one quarantined transaction."""
        return ops.explain_quarantined_record(batch_id, transaction_id)

    return server


def main() -> None:
    build_mcp_server().run()


if __name__ == "__main__":
    main()
