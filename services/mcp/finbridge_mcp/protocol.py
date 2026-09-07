"""Small dependency-free MCP stdio server for the PASS 5 read-only tools.

It implements the JSON-RPC methods needed by the candidate demo: `initialize`, `ping`, `tools/list`
and `tools/call`. Keeping transport dependency-free makes the golden path deterministic and runnable
without an API key or package registry. The business tool implementation remains separate and can be
wrapped by the official MCP SDK later without changing tool semantics.
"""

from __future__ import annotations

import json
import sys
from io import TextIOBase
from typing import Any, Mapping

from .contracts import TOOL_SPECS
from .operations import OperationsService, ToolCallError


SERVER_NAME = "finbridge-read-only-operations"
SERVER_VERSION = "0.5.0"
PROTOCOL_VERSION = "2025-06-18"


class McpProtocolServer:
    def __init__(self, operations: OperationsService) -> None:
        self._operations = operations

    def _result(self, request_id: object, result: Mapping[str, object]) -> dict[str, object]:
        return {"jsonrpc": "2.0", "id": request_id, "result": dict(result)}

    def _error(self, request_id: object, code: int, message: str) -> dict[str, object]:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }

    def handle(self, request: Mapping[str, object]) -> dict[str, object] | None:
        if request.get("jsonrpc") != "2.0":
            return self._error(request.get("id"), -32600, "Invalid JSON-RPC version")
        method = request.get("method")
        request_id = request.get("id")
        if not isinstance(method, str):
            return self._error(request_id, -32600, "Missing method")
        if method.startswith("notifications/"):
            return None
        if method == "initialize":
            return self._result(
                request_id,
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    "instructions": (
                        "FinBridge PASS 5 exposes only read-only persisted operations evidence. "
                        "No mutation, SQL, shell or finance-decision tools are available."
                    ),
                },
            )
        if method == "ping":
            return self._result(request_id, {})
        if method == "tools/list":
            return self._result(request_id, {"tools": [tool.as_mcp_dict() for tool in TOOL_SPECS]})
        if method == "tools/call":
            params = request.get("params")
            if not isinstance(params, dict):
                return self._error(request_id, -32602, "tools/call params must be an object")
            name = params.get("name")
            arguments = params.get("arguments", {})
            if not isinstance(name, str) or not isinstance(arguments, dict):
                return self._error(request_id, -32602, "Invalid tools/call name or arguments")
            try:
                evidence = self._operations.call_tool(name, arguments)
            except ToolCallError as exc:
                return self._result(
                    request_id,
                    {
                        "content": [{"type": "text", "text": str(exc)}],
                        "isError": True,
                    },
                )
            text = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            return self._result(
                request_id,
                {
                    "content": [{"type": "text", "text": text}],
                    "structuredContent": evidence,
                    "isError": False,
                },
            )
        return self._error(request_id, -32601, f"Method not found: {method}")

    def serve_lines(self, source: TextIOBase, sink: TextIOBase) -> None:
        for line in source:
            if not line.strip():
                continue
            try:
                request = json.loads(line)
                if not isinstance(request, dict):
                    raise ValueError("request must be an object")
                response = self.handle(request)
            except (json.JSONDecodeError, ValueError) as exc:
                response = self._error(None, -32700, f"Parse error: {exc}")
            if response is not None:
                sink.write(json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n")
                sink.flush()

    def serve_stdio(self) -> None:
        self.serve_lines(sys.stdin, sys.stdout)
