from __future__ import annotations

import unittest
from dataclasses import dataclass

from finbridge_domain.contracts import FROZEN_SCENARIO
from finbridge_domain.fixtures import build_synthetic_legacy_batch
from finbridge_storage.factory import AZURITE_CONNECTION_STRING, build_azurite_storage


@dataclass
class _BlobItem:
    name: str


class _Download:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def readall(self) -> bytes:
        return self._data


class _BlobClient:
    def __init__(self, container: "_ContainerClient", name: str) -> None:
        self._container = container
        self._name = name

    def exists(self) -> bool:
        return self._name in self._container.blobs

    def upload_blob(self, data: bytes, *, overwrite: bool) -> None:
        if not overwrite and self.exists():
            raise RuntimeError("blob exists")
        self._container.blobs[self._name] = bytes(data)

    def download_blob(self) -> _Download:
        return _Download(self._container.blobs[self._name])


class _ContainerClient:
    def __init__(self) -> None:
        self.created = False
        self.blobs: dict[str, bytes] = {}

    def exists(self) -> bool:
        return self.created

    def create_container(self) -> None:
        self.created = True

    def get_blob_client(self, name: str) -> _BlobClient:
        return _BlobClient(self, name)

    def list_blobs(self, *, name_starts_with: str = "") -> list[_BlobItem]:
        return [_BlobItem(name) for name in sorted(self.blobs) if name.startswith(name_starts_with)]


class _ServiceClient:
    def __init__(self) -> None:
        self.containers: dict[str, _ContainerClient] = {}

    def get_container_client(self, name: str) -> _ContainerClient:
        return self.containers.setdefault(name, _ContainerClient())


class AzuriteAdapterContractTests(unittest.TestCase):
    def test_azurite_factory_uses_four_required_blob_surfaces(self) -> None:
        fake = _ServiceClient()
        storage = build_azurite_storage(AZURITE_CONNECTION_STRING, service_client=fake)
        batch = build_synthetic_legacy_batch()
        storage.raw.put(FROZEN_SCENARIO.batch_id, batch)
        storage.processed.put(FROZEN_SCENARIO.batch_id, batch[:1])
        storage.quarantine.put(FROZEN_SCENARIO.batch_id, batch[-1:], ())
        storage.audit.list_events(FROZEN_SCENARIO.batch_id)

        self.assertEqual(set(fake.containers), {"raw", "processed", "quarantine", "audit"})
        self.assertTrue(all(container.created for container in fake.containers.values()))
        self.assertEqual(storage.raw.get(FROZEN_SCENARIO.batch_id), batch)


if __name__ == "__main__":
    unittest.main()
