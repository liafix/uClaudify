"""Azure Functions v2 trigger adapter for FinBridge PASS 3.

This module contains no finance/data-quality decision logic. It wires a raw Blob trigger to the
framework-free processing handler and builds the same blob-backed storage ports used by Azurite.
"""

from __future__ import annotations

import os

try:
    import azure.functions as func  # type: ignore[import-not-found]
except ModuleNotFoundError:  # repository tests compile without Azure runtime packages
    func = None  # type: ignore[assignment]

from batch_processor.handler import process_raw_blob
from finbridge_storage.factory import build_azure_storage


if func is not None:
    app = func.FunctionApp()

    @app.function_name(name="FinBridgeBatchProcessor")
    @app.blob_trigger(
        arg_name="input_blob",
        path="raw/{name}",
        connection="FINBRIDGE_STORAGE",
    )
    def process_batch(input_blob: "func.InputStream") -> None:
        connection_string = os.environ.get("FINBRIDGE_STORAGE")
        if not connection_string:
            raise RuntimeError("FINBRIDGE_STORAGE connection string is required")
        process_raw_blob(input_blob.read(), build_azure_storage(connection_string))
