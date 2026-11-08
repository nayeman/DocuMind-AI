"""Unit tests for Azure AI Search vector indexing and similarity retrieval."""

from unittest.mock import MagicMock

import pytest

from documind.clients.ai_search import AISearchClient
from documind.config.settings import Settings


@pytest.mark.asyncio
async def test_ai_search_client_indexing_and_search() -> None:
    """Verify AI Search schema creation, chunk upload, and vector query."""
    mock_index_client = MagicMock()
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
    mock_index_client.create_or_update_index.assert_called_once()

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

    purged = await client.delete_expired_chunks(max_age_hours=24)
    assert purged == 1
    mock_search_client.delete_documents.assert_called_once_with(documents=[{"chunk_id": "c1"}])
