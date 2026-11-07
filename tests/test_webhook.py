"""Tests for WhatsApp Cloud API webhook endpoints and signature verification."""

import pytest
from httpx import ASGITransport, AsyncClient

from documind.config.settings import get_settings
from documind.main import app


@pytest.fixture(autouse=True)
def configure_test_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure test settings are predictably configured."""
    monkeypatch.setenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "test-verify-token-xyz")
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "test-access-token-123")
    monkeypatch.setenv("APP_ENV", "test")
    # Clear lru_cache for get_settings
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Verify health check endpoint returns 200 OK."""
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
                "hub.verify_token": "test-verify-token-xyz",
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
async def test_webhook_post_invalid_signature_in_prod(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify POST /webhook returns 403 if signature is invalid."""
    monkeypatch.setenv("APP_ENV", "prod")
    get_settings.cache_clear()

    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "12345",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [],
                        },
                    }
                ],
            }
        ],
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/webhook",
            json=payload,
            headers={"X-Hub-Signature-256": "sha256=invalid_hash_signature"},
        )
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_webhook_post_missing_signature_in_prod(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify POST /webhook returns 403 if signature header is missing in production."""
    monkeypatch.setenv("APP_ENV", "prod")
    get_settings.cache_clear()

    payload = {"object": "whatsapp_business_account", "entry": []}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post("/webhook", json=payload)
        assert response.status_code == 403
