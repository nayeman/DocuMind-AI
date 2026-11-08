"""Unit tests for RAGService using duck-typed test doubles."""

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
    f = foundry or FakeFoundry()
    s = search or FakeSearch()
    return RAGService(foundry=f, search=s)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_rag_returns_answer_when_chunks_found() -> None:
    service = _make_service()
    answer = await service.answer(
        question="¿De qué trata el documento?",
        user_phone="+573001234567",
    )
    assert answer == "respuesta de prueba"


@pytest.mark.asyncio
async def test_rag_returns_no_docs_message_when_store_empty() -> None:
    empty_search = FakeSearch(chunks=[])
    service = _make_service(search=empty_search)
    answer = await service.answer(
        question="¿Qué dice el informe?",
        user_phone="+573001234567",
    )
    assert "No encontré documentos relevantes" in answer


@pytest.mark.asyncio
async def test_rag_uses_fallback_chunks_below_threshold() -> None:
    low_score_chunks = [
        {"filename": "doc.pdf", "page": 1, "text": "texto débil", "score": 0.40}
    ]
    search = FakeSearch(chunks=low_score_chunks)
    foundry = FakeFoundry(answer="Respuesta generada con contexto disponible")
    service = _make_service(foundry=foundry, search=search)

    answer = await service.answer(
        question="Pregunta poco relevante",
        user_phone="+573001234567",
    )
    assert answer == "Respuesta generada con contexto disponible"


@pytest.mark.asyncio
async def test_rag_raises_service_error_on_llm_failure() -> None:
    service = _make_service(foundry=ErrorFoundry())
    with pytest.raises(RAGServiceError):
        await service.answer(
            question="¿Qué dice el documento?",
            user_phone="+573001234567",
        )
