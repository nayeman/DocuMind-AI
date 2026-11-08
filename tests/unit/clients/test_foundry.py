"""Unit tests for FoundryClient (Azure OpenAI chat completions and embeddings)."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from openai import RateLimitError

from documind.clients.foundry import FoundryClient
from documind.config.settings import Settings


@pytest.mark.asyncio
async def test_foundry_client_chat_and_embeddings() -> None:
    """Verify chat completion and embeddings calls."""
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
async def test_foundry_client_retry_on_rate_limit() -> None:
    """Verify tenacity exponential retry on RateLimitError."""
    mock_openai = AsyncMock()
    mock_emb_item = MagicMock(embedding=[0.5] * 5, index=0)
    mock_emb_res = MagicMock(data=[mock_emb_item])

    mock_response = MagicMock(status_code=429, headers={})
    rate_limit_err = RateLimitError("Rate limit exceeded", response=mock_response, body=None)
    mock_openai.embeddings.create.side_effect = [rate_limit_err, mock_emb_res]

    client = FoundryClient(
        settings=Settings(
            azure_openai_embedding_deployment="text-emb",
        ),
        client=mock_openai,
    )

    result = await client.get_embeddings_batch(["texto de prueba"])
    assert len(result) == 1
    assert mock_openai.embeddings.create.call_count == 2

