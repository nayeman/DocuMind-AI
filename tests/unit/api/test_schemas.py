"""Unit tests for WhatsApp Cloud API Pydantic schemas."""

from documind.api.schemas import (
    WhatsAppMessage,
    WhatsAppWebhookPayload,
)


def test_whatsapp_text_message_schema() -> None:
    """Verify parsing a WhatsApp text message."""
    raw = {
        "from": "573001112233",
        "id": "wamid.HBgL",
        "timestamp": "1700000000",
        "type": "text",
        "text": {"body": "¿Qué dice el documento?"},
    }
    msg = WhatsAppMessage.model_validate(raw)
    assert msg.from_ == "573001112233"
    assert msg.type == "text"
    assert msg.text is not None
    assert msg.text.body == "¿Qué dice el documento?"


def test_whatsapp_document_message_schema() -> None:
    """Verify parsing a WhatsApp document message."""
    raw = {
        "from": "573001112233",
        "id": "wamid.HBgL2",
        "timestamp": "1700000000",
        "type": "document",
        "document": {
            "id": "media-id-999",
            "filename": "informe.pdf",
            "mime_type": "application/pdf",
        },
    }
    msg = WhatsAppMessage.model_validate(raw)
    assert msg.from_ == "573001112233"
    assert msg.type == "document"
    assert msg.document is not None
    assert msg.document.id == "media-id-999"
    assert msg.document.filename == "informe.pdf"


def test_whatsapp_webhook_payload_parsing() -> None:
    """Verify complete webhook payload schema parsing."""
    raw_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_ID_123",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"phone_number_id": "PN_ID"},
                            "messages": [
                                {
                                    "from": "573001112233",
                                    "id": "wamid.1",
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {"body": "Hola"},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }
    payload = WhatsAppWebhookPayload.model_validate(raw_payload)
    assert payload.object == "whatsapp_business_account"
    assert len(payload.entry) == 1
    change = payload.entry[0].changes[0]
    assert change.field == "messages"
    assert change.value.messages is not None
    assert len(change.value.messages) == 1
