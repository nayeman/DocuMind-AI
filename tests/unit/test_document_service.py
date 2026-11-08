"""Unit tests for DocumentService using duck-typed test doubles."""

import asyncio
from typing import Any

import pytest

from documind.config.settings import Settings
from documind.processing.chunking import TextChunker
from documind.processing.extraction import TextExtractor
from documind.services.documents import (
    DocumentService,
    FileTooLargeError,
    UnsupportedFileExtensionError,
)


class FakeWhatsApp:
    def __init__(self, media_bytes: bytes = b"fake pdf content"):
        self._media_bytes = media_bytes
        self.sent_messages: list[str] = []

    async def send_text_message(self, to: str, body: str) -> dict[str, Any]:
        self.sent_messages.append(body)
        return {"status": "sent"}

    async def send_typing_indicator(self, to: str, message_id: str | None = None) -> dict[str, Any]:
        return {"status": "indicator_sent"}

    async def download_media(self, media_id: str) -> bytes:
        return self._media_bytes


class FakeBlob:
    async def ensure_container(self) -> None:
        pass

    async def upload_document(
        self, user_phone: str, document_id: str, filename: str, content: bytes
    ) -> str:
        return f"https://fake.blob.core.windows.net/{user_phone}/{document_id}/{filename}"

    async def download_document(self, blob_path: str) -> bytes:
        return b""


class FakeSearch:
    def __init__(self) -> None:
        self.indexed_chunks: list[dict[str, Any]] = []

    async def ensure_index(self) -> None:
        pass

    async def index_chunks(self, chunks: list[dict[str, Any]], user_phone: str) -> None:
        self.indexed_chunks.extend(chunks)

    async def search(
        self, query_embedding: list[float], user_phone: str, top_k: int = 5
    ) -> list[dict[str, Any]]:
        return []

    async def delete_expired_chunks(self, max_age_hours: int | None = None) -> int:
        return 0


class FakeFoundry:
    async def get_embedding(self, text: str) -> list[float]:
        return [0.1] * 10

    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 10 for _ in texts]

    async def chat_completion(
        self, messages: list[dict[str, str]], temperature: float = 0.1
    ) -> str:
        return ""


_TXT_CONTENT = b"Este es el contenido del documento de prueba."


def _make_service(
    media_bytes: bytes = _TXT_CONTENT,
    max_file_size_mb: int = 20,
) -> tuple[DocumentService, FakeSearch]:
    store = FakeSearch()
    settings = Settings(
        max_file_size_mb=max_file_size_mb,
        allowed_extensions=["pdf", "docx", "txt"],
    )
    service = DocumentService(
        settings=settings,
        whatsapp=FakeWhatsApp(media_bytes=media_bytes),  # type: ignore[arg-type]
        storage=FakeBlob(),  # type: ignore[arg-type]
        search=store,  # type: ignore[arg-type]
        foundry=FakeFoundry(),  # type: ignore[arg-type]
        chunker=TextChunker(chunk_size=50, chunk_overlap=5),
        extractor=TextExtractor(),
    )
    return service, store


def test_process_txt_document_indexes_chunks() -> None:
    service, store = _make_service(media_bytes=_TXT_CONTENT)
    result = asyncio.run(service.process_document("media_123", "test.txt", "+1234567890"))
    assert result["status"] == "indexed"
    assert result["chunk_count"] >= 1
    assert len(store.indexed_chunks) >= 1


def test_process_document_rejects_unsupported_extension() -> None:
    service, _ = _make_service()
    with pytest.raises(UnsupportedFileExtensionError):
        asyncio.run(service.process_document("media_123", "malware.exe", "+1234567890"))


def test_process_document_rejects_file_too_large() -> None:
    big_content = b"x" * (2 * 1024 * 1024)
    service, _ = _make_service(media_bytes=big_content, max_file_size_mb=1)
    with pytest.raises(FileTooLargeError):
        asyncio.run(service.process_document("media_123", "big.txt", "+1234567890"))
