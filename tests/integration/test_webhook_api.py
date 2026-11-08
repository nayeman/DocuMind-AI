"""Integration tests for WhatsApp Webhook API endpoints and security layer."""

import hashlib
import hmac

import pytest
from httpx import ASGITransport, AsyncClient

from documind.main import app


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Verify health check endpoint returns 200 OK and valid JSON body."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


@pytest.mark.asyncio
async def test_webhook_verification_success() -> None:
    """Verify GET /webhook succeeds with matching verify_token and returns challenge."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "mock-test-verify-token",
                "hub.challenge": "1158201444",
            },
        )
        assert response.status_code == 200
        assert response.text == "1158201444"


@pytest.mark.asyncio
async def test_webhook_verification_failure() -> None:
    """Verify GET /webhook returns 403 when verify_token does not match."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get(
            "/webhook",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong-token-abc",
                "hub.challenge": "1158201444",
            },
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_webhook_post_invalid_signature() -> None:
    """Verify POST /webhook returns 403 when signature is invalid."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/webhook",
            headers={"X-Hub-Signature-256": "sha256=invalidsignature"},
            content=b'{"object": "whatsapp_business_account"}',
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_webhook_post_missing_signature() -> None:
    """Verify POST /webhook returns 403 when signature header is missing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/webhook",
            content=b'{"object": "whatsapp_business_account"}',
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_webhook_post_valid_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify POST /webhook accepts and queues valid WhatsApp message payload."""
    from unittest.mock import AsyncMock

    mock_handler = AsyncMock()
    monkeypatch.setattr("documind.api.whatsapp_webhook.handle_text_message", mock_handler)

    body = b"""{
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WABA_ID",
            "changes": [{
                "field": "messages",
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"phone_number_id": "PN_ID"},
                    "messages": [{
                        "from": "573001112233",
                        "id": "wamid.123",
                        "timestamp": "1700000000",
                        "type": "text",
                        "text": {"body": "Hola asistente"}
                    }]
                }
            }]
        }]
    }"""
    secret = "mock-test-app-secret"
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/webhook",
            headers={"X-Hub-Signature-256": signature},
            content=body,
        )
        assert response.status_code == 200
        assert response.json() == {"status": "received"}
    mock_handler.assert_called_once()
