from __future__ import annotations

import json
import unittest

from finbridge_domain.contracts import FROZEN_SCENARIO
from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_mcp import McpProtocolServer, OperationsService
from finbridge_processing import ProcessingOrchestrator
from finbridge_storage import build_in_memory_storage


class Pass5McpProtocolTests(unittest.TestCase):
    def setUp(self) -> None:
        storage = build_in_memory_storage()
        ProcessingOrchestrator(storage).run_golden_path(build_synthetic_legacy_batch())
        self.server = McpProtocolServer(OperationsService(storage))
        self.batch_id = FROZEN_SCENARIO.batch_id

    def test_initialize_advertises_tools_only(self) -> None:
        response = self.server.handle(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        )
        assert response is not None
        result = response["result"]
        self.assertEqual(result["capabilities"], {"tools": {"listChanged": False}})
        self.assertNotIn("prompts", result["capabilities"])
        self.assertNotIn("resources", result["capabilities"])

    def test_tools_list_is_exactly_six_read_only_tools(self) -> None:
        response = self.server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        assert response is not None
        names = [tool["name"] for tool in response["result"]["tools"]]
        self.assertEqual(
            names,
            [
                "get_batch_status",
                "get_data_quality_summary",
                "list_batch_anomalies",
                "trace_transaction",
                "get_reconciliation_result",
                "explain_quarantined_record",
            ],
        )

    def test_tools_call_returns_structured_persisted_evidence(self) -> None:
        response = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_reconciliation_result",
                    "arguments": {"batch_id": self.batch_id},
                },
            }
        )
        assert response is not None
        result = response["result"]
        self.assertIs(result["isError"], False)
        self.assertEqual(result["structuredContent"]["difference_eur"], "0.00")
        decoded = json.loads(result["content"][0]["text"])
        self.assertEqual(decoded, result["structuredContent"])

    def test_mutation_tool_is_not_exposed_and_fails_closed(self) -> None:
        response = self.server.handle(
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "delete_batch", "arguments": {"batch_id": self.batch_id}},
            }
        )
        assert response is not None
        self.assertIs(response["result"]["isError"], True)
        self.assertIn("Unknown or non-read-only tool", response["result"]["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
