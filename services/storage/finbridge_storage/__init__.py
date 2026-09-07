"""PASS 3 storage abstractions and Azure/Azurite implementations."""

from .blob_backend import AzureBlobBackend, InMemoryBlobBackend
from .blob_stores import StorageConflictError, build_blob_storage
from .factory import AZURITE_CONNECTION_STRING, build_azure_storage, build_azurite_storage, build_in_memory_storage
from .ports import AuditEvent, AuditStore, ProcessedBatchStore, QuarantineStore, RawBatchStore, StorageBundle

__all__ = [
    "AZURITE_CONNECTION_STRING",
    "AuditEvent",
    "AuditStore",
    "AzureBlobBackend",
    "InMemoryBlobBackend",
    "ProcessedBatchStore",
    "QuarantineStore",
    "RawBatchStore",
    "StorageBundle",
    "StorageConflictError",
    "build_azure_storage",
    "build_azurite_storage",
    "build_blob_storage",
    "build_in_memory_storage",
]
