"""Client adapters for external Azure and Meta services."""

from documind.clients.ai_search import AISearchClient, AISearchError
from documind.clients.azure_credential import resolve_azure_credential
from documind.clients.blob_storage import BlobStorageClient, BlobStorageError
from documind.clients.foundry import FoundryClient, FoundryClientError
from documind.clients.whatsapp import (
    MediaDownloadError,
    WhatsAppAPIError,
    WhatsAppClient,
    WhatsAppError,
)

__all__ = [
    "AISearchClient",
    "AISearchError",
    "BlobStorageClient",
    "BlobStorageError",
    "FoundryClient",
    "FoundryClientError",
    "MediaDownloadError",
    "WhatsAppAPIError",
    "WhatsAppClient",
    "WhatsAppError",
    "resolve_azure_credential",
]
