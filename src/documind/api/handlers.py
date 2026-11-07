"""Background task handlers for WhatsApp webhook events."""

import structlog

from documind.api.schemas import WhatsAppDocument
from documind.clients.whatsapp import WhatsAppClient
from documind.services.documents import DocumentProcessingError, DocumentService
from documind.services.rag import RAGService

logger = structlog.get_logger(__name__)

_QUESTION_LOG_PREVIEW_LEN = 50


async def handle_document_message(
    document: WhatsAppDocument,
    user_phone: str,
    doc_service: DocumentService | None = None,
    wa_client: WhatsAppClient | None = None,
) -> None:
    """Background handler to download, process, chunk, and index incoming document."""
    log = logger.bind(user_phone=user_phone, media_id=document.id)
    doc_service = doc_service or DocumentService()
    wa_client = wa_client or WhatsAppClient()

    filename = document.filename or f"doc_{document.id}.pdf"
    log.info("Processing incoming document", filename=filename)

    try:
        await wa_client.send_text_message(
            to=user_phone,
            body=f"📄 Hemos recibido tu documento *{filename}*. Lo estamos procesando...",
        )
        result = await doc_service.process_document(
            media_id=document.id, filename=filename, user_phone=user_phone
        )
        chunk_count = result.get("chunk_count", 0)
        await wa_client.send_text_message(
            to=user_phone,
            body=(
                f"✅ Documento *{filename}* procesado con éxito ({chunk_count} fragmentos).\n\n"
                "¡Ya puedes hacerme preguntas sobre su contenido!"
            ),
        )
        log.info("Document successfully processed and indexed", result=result)
    except DocumentProcessingError as exc:
        log.error("Failed to process incoming document", exc_info=exc)
        await wa_client.send_text_message(
            to=user_phone,
            body=f"❌ Ocurrió un error al procesar el documento *{filename}*: {exc}",
        )


async def handle_text_message(
    question: str,
    user_phone: str,
    rag_service: RAGService | None = None,
    wa_client: WhatsAppClient | None = None,
) -> None:
    """Background handler to answer question using RAG and reply via WhatsApp."""
    log = logger.bind(user_phone=user_phone, question=question[:_QUESTION_LOG_PREVIEW_LEN])
    rag_service = rag_service or RAGService()
    wa_client = wa_client or WhatsAppClient()

    log.info("Processing incoming question")

    try:
        await wa_client.send_typing_indicator(to=user_phone)
        answer = await rag_service.answer(question=question, user_phone=user_phone)
        await wa_client.send_text_message(to=user_phone, body=answer)
        log.info("Sent RAG answer to user")
    except Exception as exc:  # noqa: BLE001 — broad catch intentional for user-facing WhatsApp fallback
        log.error("Failed to answer question via RAG", exc_info=exc)
        await wa_client.send_text_message(
            to=user_phone,
            body=(
                "❌ Ocurrió un error al buscar la respuesta en tus documentos. Inténtalo de nuevo."
            ),
        )
