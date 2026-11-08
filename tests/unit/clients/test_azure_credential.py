"""Unit tests for Azure credential resolution."""

from azure.identity import ClientSecretCredential, DefaultAzureCredential

from documind.clients.azure_credential import resolve_azure_credential
from documind.config.settings import Settings


def test_resolve_azure_credential_service_principal() -> None:
    """Verify Service Principal credential is created when all 3 credentials exist."""
    settings = Settings(
        azure_client_id="dummy-client",
        azure_client_secret="dummy-secret",
        azure_tenant_id="dummy-tenant",
    )
    cred = resolve_azure_credential(settings)
    assert isinstance(cred, ClientSecretCredential)


def test_resolve_azure_credential_default_fallback() -> None:
    """Verify DefaultAzureCredential fallback when Service Principal fields are empty."""
    settings = Settings(
        azure_client_id="",
        azure_client_secret="",
        azure_tenant_id="",
    )
    cred = resolve_azure_credential(settings)
    assert isinstance(cred, DefaultAzureCredential)
