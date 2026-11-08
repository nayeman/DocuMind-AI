"""Unit tests for chunk embeddings computation."""

from unittest.mock import AsyncMock

import pytest

from documind.clients.foundry import FoundryClient
from documind.processing.embeddings import embed_chunks


@pytest.mark.asyncio
async def test_embed_chunks_populates_embedding_field() -> None:
    """Verify embed_chunks batches texts and populates embeddings on each chunk."""
    mock_foundry = AsyncMock(spec=FoundryClient)
    mock_foundry.get_embeddings_batch.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]

    chunks = [
        {"chunk_id": "c1", "text": "primer chunk"},
        {"chunk_id": "c2", "text": "segundo chunk"},
    ]

    result = await embed_chunks(chunks=chunks, foundry=mock_foundry, batch_size=10)

    assert len(result) == 2
    assert result[0]["embedding"] == [0.1, 0.2, 0.3]
    assert result[1]["embedding"] == [0.4, 0.5, 0.6]
    mock_foundry.get_embeddings_batch.assert_called_once_with(["primer chunk", "segundo chunk"])


@pytest.mark.asyncio
async def test_embed_chunks_empty_list() -> None:
    """Verify embed_chunks with empty list returns empty without calling client."""
    mock_foundry = AsyncMock(spec=FoundryClient)
    result = await embed_chunks(chunks=[], foundry=mock_foundry)
    assert result == []
    mock_foundry.get_embeddings_batch.assert_not_called()

