"""Text chunking module with token-aware splitting using tiktoken."""

from typing import Any

import structlog
import tiktoken

from documind.config.settings import Settings, get_settings

logger = structlog.get_logger(__name__)


class TextChunker:
    """Splits document pages into token-bounded chunks preserving page provenance."""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        settings: Settings | None = None,
    ) -> None:
        cfg = settings or get_settings()
        self.chunk_size = chunk_size or cfg.chunk_size
        self.chunk_overlap = chunk_overlap or cfg.chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

    def chunk(
        self, pages: list[dict[str, Any]], document_id: str, filename: str
    ) -> list[dict[str, Any]]:
        """Split document pages into sized token chunks.

        Args:
            pages: List of page dictionaries [{"page": int, "text": str}, ...].
            document_id: Unique identifier for the parent document.
            filename: Original document filename.

        Returns:
            List of chunk dictionaries formatted as:
            [
                {
                    "chunk_id": "doc_id_0000",
                    "document_id": "doc_id",
                    "filename": "file.pdf",
                    "page": 1,
                    "text": "...",
                    "token_count": 128
                },
                ...
            ]
        """
        log = logger.bind(document_id=document_id, filename=filename, pages_count=len(pages))
        log.info("Starting document chunking process")

        chunks: list[dict[str, Any]] = []
        chunk_index = 0
        step = self.chunk_size - self.chunk_overlap

        for page_info in pages:
            page_num = page_info.get("page", 1)
            raw_text = page_info.get("text", "").strip()

            if not raw_text:
                continue

            tokens = self.encoding.encode(raw_text)
            total_tokens = len(tokens)

            if total_tokens <= self.chunk_size:
                chunks.append(
                    {
                        "chunk_id": f"{document_id}_{chunk_index:04d}",
                        "document_id": document_id,
                        "filename": filename,
                        "page": page_num,
                        "text": raw_text,
                        "token_count": total_tokens,
                    }
                )
                chunk_index += 1
            else:
                start = 0
                while start < total_tokens:
                    end = min(start + self.chunk_size, total_tokens)
                    chunk_tokens = tokens[start:end]
                    chunk_text = self.encoding.decode(chunk_tokens).strip()

                    if chunk_text:
                        chunks.append(
                            {
                                "chunk_id": f"{document_id}_{chunk_index:04d}",
                                "document_id": document_id,
                                "filename": filename,
                                "page": page_num,
                                "text": chunk_text,
                                "token_count": len(chunk_tokens),
                            }
                        )
                        chunk_index += 1

                    if end >= total_tokens:
                        break
                    start += step

        log.info("Chunking completed", total_chunks=len(chunks))
        return chunks
