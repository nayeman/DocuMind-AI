"""Integration tests for WhatsApp event background handlers."""

from unittest.mock import AsyncMock

import pytest

from documind.api.handlers import handle_document_message, handle_text_message
from documind.api.schemas import WhatsAppDocument
from documind.clients.whatsapp import WhatsAppClient
from documind.services.documents import DocumentService
from documind.services.rag import RAGService


@pytest.mark.asyncio
async def test_handle_document_message_success() -> None:
    """Verify handle_document_message pipeline notifies user and delegates ingestion."""
    mock_wa = AsyncMock(spec=WhatsAppClient)
    mock_doc_service = AsyncMock(spec=DocumentService)
    mock_doc_service.process_document.return_value = {
        "status": "indexed",
        "chunk_count": 3,
        "document_id": "doc-123",
    }

    doc = WhatsAppDocument(id="media-456", filename="test.pdf")
    await handle_document_message(
        document=doc,
        user_phone="+573001112233",
        doc_service=mock_doc_service,
        wa_client=mock_wa,
    )

    mock_doc_service.process_document.assert_called_once_with(
        media_id="media-456",
        filename="test.pdf",
        user_phone="+573001112233",
    )
    # Should send processing message and confirmation message
    assert mock_wa.send_text_message.call_count == 2


@pytest.mark.asyncio
async def test_handle_text_message_success() -> None:
    """Verify handle_text_message pipeline queries RAG and sends reply."""
    mock_wa = AsyncMock(spec=WhatsAppClient)
    mock_rag = AsyncMock(spec=RAGService)
    mock_rag.answer.return_value = "El documento explica los beneficios de la nube."

    await handle_text_message(
        question="¿Qué dice sobre la nube?",
        user_phone="+573001112233",
        rag_service=mock_rag,
        wa_client=mock_wa,
    )

    mock_wa.send_typing_indicator.assert_called_once_with(to="+573001112233")
    mock_rag.answer.assert_called_once_with(
        question="¿Qué dice sobre la nube?",
        user_phone="+573001112233",
    )
    mock_wa.send_text_message.assert_called_once_with(
        to="+573001112233",
        body="El documento explica los beneficios de la nube.",
    )
