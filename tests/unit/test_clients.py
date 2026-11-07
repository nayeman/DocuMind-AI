"""Unit tests for Azure and third-party API clients using mocks."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.identity import ClientSecretCredential, DefaultAzureCredential

from documind.clients.ai_search import AISearchClient
from documind.clients.azure_credential import resolve_azure_credential
from documind.clients.blob_storage import BlobStorageClient
from documind.clients.foundry import FoundryClient
from documind.clients.whatsapp import WhatsAppClient
from documind.config.settings import Settings


def test_resolve_azure_credential_service_principal() -> None:
    settings = Settings(
        azure_client_id="dummy-client",
        azure_client_secret="dummy-secret",
        azure_tenant_id="dummy-tenant",
    )
    cred = resolve_azure_credential(settings)
    assert isinstance(cred, ClientSecretCredential)


def test_resolve_azure_credential_default_fallback() -> None:
    settings = Settings(
        azure_client_id="",
        azure_client_secret="",
        azure_tenant_id="",
    )
    cred = resolve_azure_credential(settings)
    assert isinstance(cred, DefaultAzureCredential)


@pytest.mark.asyncio
async def test_blob_storage_client_upload_and_download() -> None:
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


@pytest.mark.asyncio
async def test_ai_search_client_indexing_and_search() -> None:
    mock_index_client = MagicMock()
    mock_index_client.list_index_names.return_value = ["other-index"]

    mock_search_client = MagicMock()
    mock_upload_res = MagicMock()
    mock_upload_res.succeeded = True
    mock_search_client.upload_documents.return_value = [mock_upload_res]

    mock_search_client.search.return_value = [
        {
            "chunk_id": "c1",
            "document_id": "d1",
            "filename": "f1.pdf",
            "page": 1,
            "text": "sample text",
            "token_count": 10,
            "@search.score": 0.95,
        }
    ]

    client = AISearchClient(
        settings=Settings(azure_search_index_name="my-index"),
        index_client=mock_index_client,
        search_client=mock_search_client,
    )

    await client.ensure_index()
    mock_index_client.create_index.assert_called_once()

    chunks = [
        {
            "chunk_id": "c1",
            "document_id": "d1",
            "filename": "f1.pdf",
            "page": 1,
            "text": "sample text",
            "token_count": 10,
            "embedding": [0.1] * 1536,
        }
    ]
    await client.index_chunks(chunks, user_phone="+573001112233")
    mock_search_client.upload_documents.assert_called_once()

    results = await client.search(query_embedding=[0.1] * 1536, user_phone="+573001112233")
    assert len(results) == 1
    assert results[0]["chunk_id"] == "c1"
    assert results[0]["score"] == 0.95


@pytest.mark.asyncio
async def test_foundry_client_chat_and_embeddings() -> None:
    mock_openai = AsyncMock()

    mock_choice = MagicMock()
    mock_choice.message.content = "Respuesta del modelo"
    mock_chat_res = MagicMock(choices=[mock_choice], usage=MagicMock(total_tokens=42))
    mock_openai.chat.completions.create.return_value = mock_chat_res

    mock_emb_item = MagicMock(embedding=[0.2] * 5, index=0)
    mock_emb_res = MagicMock(data=[mock_emb_item])
    mock_openai.embeddings.create.return_value = mock_emb_res

    client = FoundryClient(
        settings=Settings(
            azure_openai_chat_deployment="gpt-4o",
            azure_openai_embedding_deployment="text-emb",
        ),
        client=mock_openai,
    )

    chat_reply = await client.chat_completion([{"role": "user", "content": "hola"}])
    assert chat_reply == "Respuesta del modelo"

    single_emb = await client.get_embedding("texto de prueba")
    assert len(single_emb) == 5

    batch_emb = await client.get_embeddings_batch(["texto1"])
    assert len(batch_emb) == 1
    assert len(batch_emb[0]) == 5


@pytest.mark.asyncio
async def test_whatsapp_client_send_message(httpx_mock) -> None:  # type: ignore[no-untyped-def]
    settings = Settings(
        whatsapp_phone_number_id="12345",
        whatsapp_access_token="secret_token",
        whatsapp_api_version="v20.0",
    )
    httpx_mock.add_response(
        url=f"https://graph.facebook.com/{settings.whatsapp_api_version}/12345/messages",
        method="POST",
        json={"messages": [{"id": "wamid.123"}]},
        status_code=200,
    )

    client = WhatsAppClient(settings=settings)
    result = await client.send_text_message(to="+573001112233", body="Hola mundo")
    assert "messages" in result

