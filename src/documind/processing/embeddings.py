"""Chunk embedding utilities for DocuMind AI."""

from typing import Any

from documind.clients.foundry import FoundryClient

DEFAULT_BATCH_SIZE = 16


async def embed_chunks(
    chunks: list[dict[str, Any]],
    foundry: FoundryClient,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[dict[str, Any]]:
    """Compute and attach vector embeddings to each chunk in batches.

    Args:
        chunks: List of chunk dictionaries containing 'text'.
        foundry: Client instance capable of batch embeddings.
        batch_size: Number of texts per batch request.

    Returns:
        The same chunks list with 'embedding' field populated.
    """
    if not chunks:
        return []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [chunk["text"] for chunk in batch]
        embeddings = await foundry.get_embeddings_batch(texts)
        for chunk, embedding in zip(batch, embeddings, strict=True):
            chunk["embedding"] = embedding

    return chunks
