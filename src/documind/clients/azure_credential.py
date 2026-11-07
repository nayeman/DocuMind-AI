"""Shared Azure credential resolution following official Azure SDK guidelines."""

from azure.core.credentials import TokenCredential
from azure.identity import ClientSecretCredential, DefaultAzureCredential

from documind.config.settings import Settings


def resolve_azure_credential(settings: Settings) -> TokenCredential:
    """Return a Service Principal credential when SP vars are set, otherwise DefaultAzureCredential.

    Follows official Microsoft Entra ID authentication guidelines:
    - Service Principal if tenant, client_id, and client_secret are provided.
    - DefaultAzureCredential fallback for Managed Identity, Azure CLI, and env vars.

    Args:
        settings: Application settings with Azure identity configuration.

    Returns:
        TokenCredential instance ready for use across Azure SDK service clients.
    """
    if settings.azure_client_id and settings.azure_client_secret and settings.azure_tenant_id:
        return ClientSecretCredential(
            tenant_id=settings.azure_tenant_id,
            client_id=settings.azure_client_id,
            client_secret=settings.azure_client_secret,
        )
    return DefaultAzureCredential()
