"""Unit tests for RAGService using duck-typed test doubles."""

import asyncio
from typing import Any

import pytest

from documind.services.rag import RAGService, RAGServiceError


class FakeFoundry:
    def __init__(self, embedding: list[float] | None = None, answer: str = "respuesta de prueba"):
        self._embedding = embedding or [0.1] * 10
        self._answer = answer

    async def get_embedding(self, text: str) -> list[float]:
        return self._embedding

    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        return [self._embedding for _ in texts]

    async def chat_completion(
        self, messages: list[dict[str, str]], temperature: float = 0.1
    ) -> str:
        return self._answer


class FakeSearch:
    _DEFAULT_CHUNK = {"filename": "doc.pdf", "page": 1, "text": "contexto relevante", "score": 0.9}

    def __init__(self, chunks: list[dict[str, Any]] | None = None):
        self._chunks = [self._DEFAULT_CHUNK] if chunks is None else chunks

    async def ensure_index(self) -> None:
        pass

    async def index_chunks(self, chunks: list[dict[str, Any]], user_phone: str) -> None:
        pass

    async def search(
        self, query_embedding: list[float], user_phone: str, top_k: int = 5
    ) -> list[dict[str, Any]]:
        return self._chunks


class ErrorFoundry:
    async def get_embedding(self, text: str) -> list[float]:
        raise ConnectionError("LLM offline")

    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        raise ConnectionError("LLM offline")

    async def chat_completion(
        self, messages: list[dict[str, str]], temperature: float = 0.1
    ) -> str:
        raise ConnectionError("LLM offline")


def _make_service(
    foundry: Any = None,
    search: Any = None,
) -> RAGService:
    return RAGService(
        foundry=foundry or FakeFoundry(),  # type: ignore[arg-type]
        search=search or FakeSearch(),  # type: ignore[arg-type]
    )


def test_rag_returns_answer_when_chunks_found() -> None:
    service = _make_service(foundry=FakeFoundry(answer="La respuesta es 42."))
    result = asyncio.run(service.answer("¿Cuál es la respuesta?", "+1234567890"))
    assert result == "La respuesta es 42."


def test_rag_returns_no_docs_message_when_store_empty() -> None:
    service = _make_service(search=FakeSearch(chunks=[]))
    result = asyncio.run(service.answer("¿Algo?", "+1234567890"))
    assert "No encontré documentos" in result or "Por favor, envía" in result


def test_rag_uses_fallback_chunks_below_threshold() -> None:
    low_score_chunks = [{"filename": "doc.pdf", "page": 1, "text": "contexto", "score": 0.5}]
    service = _make_service(
        foundry=FakeFoundry(answer="Respuesta con chunks de baja relevancia."),
        search=FakeSearch(chunks=low_score_chunks),
    )
    result = asyncio.run(service.answer("¿Algo?", "+1234567890"))
    assert result == "Respuesta con chunks de baja relevancia."


def test_rag_raises_service_error_on_llm_failure() -> None:
    service = _make_service(foundry=ErrorFoundry())
    with pytest.raises(RAGServiceError):
        asyncio.run(service.answer("¿Algo?", "+1234567890"))
