"""WhatsApp Cloud API webhook router and verification endpoints."""

import structlog
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)

from documind.api.handlers import handle_document_message, handle_text_message
from documind.api.schemas import (
    WhatsAppDocument,
    WhatsAppMessage,
    WhatsAppText,
    WhatsAppWebhookPayload,
)
from documind.api.security import verify_meta_signature
from documind.config.settings import get_settings

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="", tags=["WhatsApp Webhook"])

_QUESTION_LOG_PREVIEW_LEN = 50


@router.get("/webhook", response_class=Response)
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
) -> Response:
    """Verification endpoint required by Meta WhatsApp Cloud API."""
    settings = get_settings()

    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_webhook_verify_token:
        logger.info("WhatsApp webhook verified successfully")
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning(
        "WhatsApp webhook verification failed",
        hub_mode=hub_mode,
        provided_token=hub_verify_token,
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch or invalid mode",
    )


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
) -> dict[str, str]:
    """Receive incoming webhook events from WhatsApp Cloud API."""
    settings = get_settings()
    raw_body = await request.body()

    app_secret = (
        settings.whatsapp_app_secret
        or settings.whatsapp_access_token
        or settings.whatsapp_webhook_verify_token
    )
    if not x_hub_signature_256:
        logger.error("Missing X-Hub-Signature-256 header")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing signature header",
        )

    if not verify_meta_signature(raw_body, x_hub_signature_256, app_secret):
        logger.error("Invalid X-Hub-Signature-256 header")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid signature",
        )

    try:
        payload_data = await request.json()
        payload = WhatsAppWebhookPayload.model_validate(payload_data)
    except Exception as exc:  # noqa: BLE001 — non-standard Meta webhook events
        logger.warning("Unrecognized or non-standard webhook payload", error=str(exc))
        return {"status": "ignored"}

    for entry in payload.entry:
        for change in entry.changes:
            messages = change.value.messages or []
            for message in messages:
                user_phone = message.from_
                if message.type == "document" and message.document:
                    logger.info(
                        "Received document message",
                        user_phone=user_phone,
                        doc_id=message.document.id,
                    )
                    background_tasks.add_task(
                        handle_document_message,
                        message.document,
                        user_phone,
                    )
                elif message.type == "text" and message.text:
                    logger.info(
                        "Received text query",
                        user_phone=user_phone,
                        text=message.text.body[:_QUESTION_LOG_PREVIEW_LEN],
                    )
                    background_tasks.add_task(
                        handle_text_message,
                        message.text.body,
                        user_phone,
                    )
                else:
                    logger.info(
                        "Received non-document/non-text message type",
                        message_type=message.type,
                        user_phone=user_phone,
                    )

    return {"status": "received"}


__all__ = [
    "WhatsAppDocument",
    "WhatsAppMessage",
    "WhatsAppText",
    "WhatsAppWebhookPayload",
    "handle_document_message",
    "handle_text_message",
    "router",
    "verify_meta_signature",
]
