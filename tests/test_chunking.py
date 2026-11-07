"""Tests for TextChunker token-based splitting."""

from documind.config.settings import Settings
from documind.processing.chunking import TextChunker


def test_chunk_creation_from_pages() -> None:
    """Test that chunks are properly created from sample pages."""
    settings = Settings(chunk_size=50, chunk_overlap=10)
    chunker = TextChunker(settings=settings)

    pages = [
        {"page": 1, "text": "Este es el primer párrafo de prueba sobre inteligencia artificial."},
        {"page": 2, "text": "En esta segunda página detallamos cómo funciona la arquitectura RAG."},
    ]
    document_id = "doc-test-123"
    filename = "test_manual.pdf"

    chunks = chunker.chunk(pages=pages, document_id=document_id, filename=filename)

    assert len(chunks) == 2
    assert chunks[0]["document_id"] == document_id
    assert chunks[0]["filename"] == filename
    assert chunks[0]["page"] == 1
    assert chunks[1]["page"] == 2


def test_chunk_id_format() -> None:
    """Test that chunk IDs strictly follow {document_id}_{index:04d} format."""
    settings = Settings(chunk_size=10, chunk_overlap=2)
    chunker = TextChunker(settings=settings)

    # Large text generating multiple chunks
    large_text = " ".join(["palabra"] * 100)
    pages = [{"page": 1, "text": large_text}]
    doc_id = "doc-uuid-456"

    chunks = chunker.chunk(pages=pages, document_id=doc_id, filename="data.txt")

    assert len(chunks) > 1
    for idx, chunk in enumerate(chunks):
        expected_id = f"{doc_id}_{idx:04d}"
        assert chunk["chunk_id"] == expected_id


def test_chunk_token_count_bounds() -> None:
    """Test that generated chunks stay within configured token bounds."""
    chunk_size = 30
    chunk_overlap = 5
    settings = Settings(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunker = TextChunker(settings=settings)

    long_page_text = " ".join(["Tokenización con Azure OpenAI y procesamiento de documentos."] * 15)
    pages = [{"page": 1, "text": long_page_text}]

    chunks = chunker.chunk(pages=pages, document_id="doc-bounds", filename="tokens.txt")

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk["token_count"] <= chunk_size


def test_chunk_empty_pages() -> None:
    """Test that empty or whitespace-only pages produce no chunks."""
    chunker = TextChunker()
    pages = [{"page": 1, "text": ""}, {"page": 2, "text": "   "}]

    chunks = chunker.chunk(pages=pages, document_id="empty-doc", filename="empty.txt")
    assert chunks == []
