"""Global pytest fixtures and configuration for DocuMind AI."""

from collections.abc import Generator

import pytest

from documind.config.settings import get_settings


@pytest.fixture(autouse=True)
def test_environment(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Provide a clean, isolated test environment for all unit and integration tests."""
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "123456789")
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "mock-test-access-token")
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "mock-test-app-secret")
    monkeypatch.setenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "mock-test-verify-token")
    monkeypatch.setenv("AZURE_STORAGE_ACCOUNT_NAME", "mockstorageaccount")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://mocksearch.search.windows.net")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://mockopenai.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o")
    monkeypatch.setenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
