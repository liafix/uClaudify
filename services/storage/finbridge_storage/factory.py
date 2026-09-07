"""Storage factories for deterministic local mode and Azure/Azurite mode."""

from __future__ import annotations

from typing import Any

from .blob_backend import AzureBlobBackend, InMemoryBlobBackend
from .blob_stores import build_blob_storage
from .ports import StorageBundle


AZURITE_CONNECTION_STRING = "UseDevelopmentStorage=true"


def build_in_memory_storage() -> StorageBundle:
    return build_blob_storage(InMemoryBlobBackend())


def build_azurite_storage(
    connection_string: str = AZURITE_CONNECTION_STRING,
    *,
    service_client: Any | None = None,
) -> StorageBundle:
    """Build the real Blob/Azurite adapter.

    The injectable client is only for adapter contract tests. Production/local-Azurite use the
    Azure SDK client constructed from the connection string.
    """

    return build_blob_storage(
        AzureBlobBackend(connection_string, service_client=service_client)
    )


def build_azure_storage(connection_string: str) -> StorageBundle:
    return build_blob_storage(AzureBlobBackend(connection_string))
