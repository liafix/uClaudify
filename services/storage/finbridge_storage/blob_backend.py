"""Blob transport implementations.

`InMemoryBlobBackend` executes the same store code during local tests. `AzureBlobBackend` is the
real Azure Storage/Azurite adapter and imports the Azure SDK lazily so the deterministic candidate
demo remains runnable without cloud dependencies.
"""

from __future__ import annotations

from typing import Any, Protocol


class BlobBackend(Protocol):
    def put(self, container: str, name: str, data: bytes) -> None: ...

    def get(self, container: str, name: str) -> bytes | None: ...

    def list_names(self, container: str, prefix: str = "") -> tuple[str, ...]: ...


class InMemoryBlobBackend:
    def __init__(self) -> None:
        self._blobs: dict[tuple[str, str], bytes] = {}

    def put(self, container: str, name: str, data: bytes) -> None:
        self._blobs[(container, name)] = bytes(data)

    def get(self, container: str, name: str) -> bytes | None:
        data = self._blobs.get((container, name))
        return bytes(data) if data is not None else None

    def list_names(self, container: str, prefix: str = "") -> tuple[str, ...]:
        return tuple(
            sorted(name for current_container, name in self._blobs if current_container == container and name.startswith(prefix))
        )


class AzureBlobBackend:
    """Azure Blob implementation compatible with Azure Storage and Azurite.

    Pass either a normal Azure Storage connection string or `UseDevelopmentStorage=true` for
    Azurite. A service-client can be injected for executable adapter tests without the SDK/service.
    """

    def __init__(self, connection_string: str, *, service_client: Any | None = None) -> None:
        self.connection_string = connection_string
        if service_client is None:
            try:
                from azure.storage.blob import BlobServiceClient  # type: ignore[import-not-found]
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "azure-storage-blob is required for Azure/Azurite runtime; install the PASS 3 Azure requirements"
                ) from exc
            service_client = BlobServiceClient.from_connection_string(connection_string)
        self._service = service_client
        self._ensured: set[str] = set()

    def _container(self, name: str) -> Any:
        container = self._service.get_container_client(name)
        if name not in self._ensured:
            # `exists()` is supported by both the Azure service and Azurite. Avoid relying on SDK
            # exception classes so this adapter remains easy to contract-test with a tiny fake.
            if not container.exists():
                container.create_container()
            self._ensured.add(name)
        return container

    def put(self, container: str, name: str, data: bytes) -> None:
        blob = self._container(container).get_blob_client(name)
        blob.upload_blob(data, overwrite=True)

    def get(self, container: str, name: str) -> bytes | None:
        blob = self._container(container).get_blob_client(name)
        if not blob.exists():
            return None
        return bytes(blob.download_blob().readall())

    def list_names(self, container: str, prefix: str = "") -> tuple[str, ...]:
        client = self._container(container)
        return tuple(sorted(item.name for item in client.list_blobs(name_starts_with=prefix)))
