"""Unit tests for WhatsApp Cloud API client."""

import pytest

from documind.clients.whatsapp import WhatsAppClient
from documind.config.settings import Settings


@pytest.mark.asyncio
async def test_whatsapp_client_send_message(httpx_mock) -> None:  # type: ignore[no-untyped-def]
    """Verify sending WhatsApp text message with mock HTTP transport."""
    settings = Settings(
        whatsapp_phone_number_id="12345",
        whatsapp_access_token="secret_token",
        whatsapp_api_version="v20.0",
    )
    httpx_mock.add_response(
        url=f"https://graph.facebook.com/{settings.whatsapp_api_version}/12345/messages",
        method="POST",
        json={"messages": [{"id": "wamid.123"}]},
        status_code=200,
    )

    client = WhatsAppClient(settings=settings)
    result = await client.send_text_message(to="+573001112233", body="Hola mundo")
    assert "messages" in result


@pytest.mark.asyncio
async def test_whatsapp_client_download_media(httpx_mock) -> None:  # type: ignore[no-untyped-def]
    """Verify downloading media bytes from WhatsApp Graph API."""
    settings = Settings(
        whatsapp_access_token="secret_token",
        whatsapp_api_version="v20.0",
    )
    media_id = "media_xyz_123"

    # Step 1: Query media URL
    httpx_mock.add_response(
        url=f"https://graph.facebook.com/{settings.whatsapp_api_version}/{media_id}",
        method="GET",
        json={"url": "https://lookaside.fbsbx.com/media/download_binary"},
        status_code=200,
    )

    # Step 2: Download raw media bytes
    httpx_mock.add_response(
        url="https://lookaside.fbsbx.com/media/download_binary",
        method="GET",
        content=b"%PDF-1.4 sample pdf content",
        status_code=200,
    )

    client = WhatsAppClient(settings=settings)
    media_bytes = await client.download_media(media_id)
    assert media_bytes == b"%PDF-1.4 sample pdf content"
