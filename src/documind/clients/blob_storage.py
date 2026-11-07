"""Azure Blob Storage client for managing original documents."""

import asyncio
from pathlib import Path

import structlog
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient

from documind.clients.azure_credential import resolve_azure_credential
from documind.config.settings import Settings, get_settings

logger = structlog.get_logger(__name__)


class BlobStorageError(Exception):
    """Base exception for Azure Blob Storage operations."""


class BlobStorageClient:
    """Manages document uploads and downloads with Azure Blob Storage."""

    def __init__(
        self,
        settings: Settings | None = None,
        blob_service_client: BlobServiceClient | None = None,
        container_name: str | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._container_name = container_name or self.settings.azure_storage_container_name

        if blob_service_client is not None:
            self._blob_service_client = blob_service_client
        else:
            credential = resolve_azure_credential(self.settings)
            account_url = (
                f"https://{self.settings.azure_storage_account_name}.blob.core.windows.net"
            )
            self._blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=credential,
            )
        self._container_client = self._blob_service_client.get_container_client(
            self._container_name
        )

    async def ensure_container(self) -> None:
        """Ensure that the target storage container exists."""
        try:
            exists = await asyncio.to_thread(self._container_client.exists)
            if not exists:
                await asyncio.to_thread(self._container_client.create_container)
                logger.info("Created blob container", container=self._container_name)
        except AzureError as exc:
            logger.error("Failed to check/create blob container", exc_info=exc)
            raise BlobStorageError(f"Container operation failed: {exc}") from exc

    async def upload_document(
        self, user_phone: str, document_id: str, filename: str, content: bytes
    ) -> str:
        """Upload raw document bytes to the user's storage path."""
        safe_filename = Path(filename).name or "document.bin"
        safe_phone = "".join(c for c in user_phone if c.isalnum() or c in "+-_")
        blob_path = f"{safe_phone}/{document_id}/{safe_filename}"
        log = logger.bind(blob_path=blob_path, size_bytes=len(content))
        log.info("Uploading document to Azure Blob Storage")

        try:
            blob_client = self._container_client.get_blob_client(blob_path)
            await asyncio.to_thread(blob_client.upload_blob, content, overwrite=True)
            blob_url = blob_client.url
            log.info("Document successfully uploaded to blob", blob_url=blob_url)
            return str(blob_url)
        except AzureError as exc:
            log.error("Failed to upload blob", exc_info=exc)
            raise BlobStorageError(f"Upload failed for {blob_path}: {exc}") from exc

    async def download_document(self, blob_path: str) -> bytes:
        """Download document bytes given its container-relative path."""
        log = logger.bind(blob_path=blob_path)
        log.info("Downloading document from Azure Blob Storage")

        try:
            blob_client = self._container_client.get_blob_client(blob_path)
            data: bytes = await asyncio.to_thread(lambda: blob_client.download_blob().readall())
            log.info("Downloaded document from blob", size_bytes=len(data))
            return data
        except AzureError as exc:
            log.error("Failed to download blob", exc_info=exc)
            raise BlobStorageError(f"Download failed for {blob_path}: {exc}") from exc
