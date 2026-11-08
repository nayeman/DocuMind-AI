"""Document ingestion and orchestration service."""

from pathlib import Path
from typing import Any
from uuid import uuid4

import structlog

from documind.clients.ai_search import AISearchClient, AISearchError
from documind.clients.blob_storage import BlobStorageClient, BlobStorageError
from documind.clients.foundry import FoundryClient, FoundryClientError
from documind.clients.whatsapp import WhatsAppClient
from documind.config.settings import Settings, get_settings
from documind.processing.chunking import TextChunker
from documind.processing.embeddings import embed_chunks
from documind.processing.extraction import TextExtractor

logger = structlog.get_logger(__name__)

_BYTES_PER_MB = 1024 * 1024


class DocumentProcessingError(Exception):
    """Base exception for document processing pipeline."""


class FileTooLargeError(DocumentProcessingError):
    """Raised when an uploaded file exceeds the configured maximum size limit."""


class UnsupportedFileExtensionError(DocumentProcessingError):
    """Raised when an uploaded file extension is not permitted."""


class DocumentService:
    """Orchestrates end-to-end document ingestion: parse, chunk, embed, and index."""

    def __init__(
        self,
        settings: Settings | None = None,
        whatsapp: WhatsAppClient | None = None,
        storage: BlobStorageClient | None = None,
        search: AISearchClient | None = None,
        foundry: FoundryClient | None = None,
        chunker: TextChunker | None = None,
        extractor: TextExtractor | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.whatsapp = whatsapp or WhatsAppClient(self.settings)
        self.storage = storage or BlobStorageClient(self.settings)
        self.search = search or AISearchClient(self.settings)
        self.foundry = foundry or FoundryClient(self.settings)
        self.chunker = chunker or TextChunker(settings=self.settings)
        self.extractor = extractor or TextExtractor()

    async def process_document(
        self, media_id: str, filename: str, user_phone: str
    ) -> dict[str, Any]:
        """Execute the ingestion pipeline for an incoming document."""
        clean_filename = Path(filename).name or f"doc_{media_id}.bin"
        log = logger.bind(user_phone=user_phone, media_id=media_id, filename=clean_filename)
        log.info("Starting document processing pipeline")

        extension = clean_filename.rsplit(".", 1)[-1].lower() if "." in clean_filename else ""
        if extension not in self.settings.allowed_extensions:
            log.warning("File extension rejected", extension=extension)
            raise UnsupportedFileExtensionError(
                f"File extension '.{extension}' is not permitted. "
                f"Allowed: {', '.join(self.settings.allowed_extensions)}"
            )

        log.info("Downloading media from WhatsApp")
        content = await self.whatsapp.download_media(media_id)

        file_size = len(content)
        if file_size > self.settings.max_file_size_bytes:
            log.warning(
                "File size limit exceeded",
                size_bytes=file_size,
                max_bytes=self.settings.max_file_size_bytes,
            )
            raise FileTooLargeError(
                f"File size ({file_size / _BYTES_PER_MB:.1f} MB) exceeds maximum allowed "
                f"{self.settings.max_file_size_mb} MB."
            )

        document_id = str(uuid4())
        log = log.bind(document_id=document_id)

        try:
            await self.storage.ensure_container()
            blob_url = await self.storage.upload_document(
                user_phone=user_phone,
                document_id=document_id,
                filename=clean_filename,
                content=content,
            )
        except BlobStorageError as exc:
            raise DocumentProcessingError(f"Storage failed for '{clean_filename}': {exc}") from exc

        pages = self.extractor.extract(content, clean_filename)
        if not pages:
            log.error("No extractable text found in document")
            raise DocumentProcessingError(f"No extractable text found in '{clean_filename}'.")

        chunks = self.chunker.chunk(pages, document_id, clean_filename)
        if not chunks:
            log.error("No chunks produced from extracted pages")
            raise DocumentProcessingError(f"No chunks could be generated for '{clean_filename}'.")

        try:
            embedded_chunks = await embed_chunks(chunks, self.foundry)
        except FoundryClientError as exc:
            msg = f"Embedding failed for '{clean_filename}': {exc}"
            raise DocumentProcessingError(msg) from exc

        try:
            await self.search.ensure_index()
            await self.search.index_chunks(embedded_chunks, user_phone)
            await self.search.delete_expired_chunks()
        except AISearchError as exc:
            raise DocumentProcessingError(f"Indexing failed for '{clean_filename}': {exc}") from exc

        summary = {
            "document_id": document_id,
            "filename": clean_filename,
            "chunk_count": len(chunks),
            "status": "indexed",
            "blob_url": blob_url,
        }
        log.info("Document pipeline finished successfully", summary=summary)
        return summary
