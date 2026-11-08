"""Unit tests for DocumentService using duck-typed test doubles."""

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
        return "fake chat response"


def _make_service(
    settings: Settings | None = None,
    media_bytes: bytes = b"contenido de prueba para documento",
) -> tuple[DocumentService, FakeWhatsApp, FakeBlob, FakeSearch]:
    cfg = settings or Settings(allowed_extensions=["pdf", "docx", "txt"], max_file_size_mb=20)
    wa = FakeWhatsApp(media_bytes=media_bytes)
    blob = FakeBlob()
    search = FakeSearch()
    foundry = FakeFoundry()
    chunker = TextChunker(settings=cfg)
    extractor = TextExtractor()

    service = DocumentService(
        settings=cfg,
        whatsapp=wa,  # type: ignore[arg-type]
        storage=blob,  # type: ignore[arg-type]
        search=search,  # type: ignore[arg-type]
        foundry=foundry,  # type: ignore[arg-type]
        chunker=chunker,
        extractor=extractor,
    )
    return service, wa, blob, search


@pytest.mark.asyncio
async def test_process_txt_document_indexes_chunks() -> None:
    service, _, _, search = _make_service(media_bytes=b"Este es un texto simple para indexar.")
    result = await service.process_document(
        media_id="media-001",
        filename="archivo.txt",
        user_phone="+573001234567",
    )
    assert result["status"] == "indexed"
    assert result["chunk_count"] > 0
    assert len(search.indexed_chunks) == result["chunk_count"]


@pytest.mark.asyncio
async def test_process_document_rejects_unsupported_extension() -> None:
    service, _, _, _ = _make_service()
    with pytest.raises(UnsupportedFileExtensionError):
        await service.process_document(
            media_id="media-002",
            filename="malicioso.exe",
            user_phone="+573001234567",
        )


@pytest.mark.asyncio
async def test_process_document_rejects_file_too_large() -> None:
    cfg = Settings(max_file_size_mb=1)
    huge_bytes = b"x" * (2 * 1024 * 1024)
    service, _, _, _ = _make_service(settings=cfg, media_bytes=huge_bytes)
    with pytest.raises(FileTooLargeError):
        await service.process_document(
            media_id="media-003",
            filename="grande.txt",
            user_phone="+573001234567",
        )
