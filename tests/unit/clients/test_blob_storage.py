"""Unit tests for Azure Blob Storage client."""

from unittest.mock import MagicMock

import pytest

from documind.clients.blob_storage import BlobStorageClient
from documind.config.settings import Settings


@pytest.mark.asyncio
async def test_blob_storage_client_upload_and_download() -> None:
    """Verify document upload and download against Azure Blob Storage."""
    mock_blob_client = MagicMock()
    mock_blob_client.url = "https://mock.blob/file.txt"
    mock_blob_client.download_blob.return_value.readall.return_value = b"blob contents"

    mock_container_client = MagicMock()
    mock_container_client.get_blob_client.return_value = mock_blob_client
    mock_container_client.exists.return_value = True

    mock_service_client = MagicMock()
    mock_service_client.get_container_client.return_value = mock_container_client

    client = BlobStorageClient(
        settings=Settings(),
        blob_service_client=mock_service_client,
        container_name="test-container",
    )

    await client.ensure_container()
    mock_container_client.exists.assert_called_once()

    url = await client.upload_document(
        user_phone="+573001112233",
        document_id="doc1",
        filename="test.pdf",
        content=b"pdf data",
    )
    assert url == "https://mock.blob/file.txt"
    mock_blob_client.upload_blob.assert_called_once_with(b"pdf data", overwrite=True)

    data = await client.download_document("path/to/blob")
    assert data == b"blob contents"
