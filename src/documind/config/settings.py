"""Application configuration and environment settings for DocuMind AI."""

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App Configuration ---
    app_env: str = Field(default="dev", description="Environment stage: dev, staging, prod")
    app_log_level: str = Field(default="INFO", description="Logging level")
    app_host: str = Field(default="0.0.0.0", description="Host address to bind the server")
    app_port: int = Field(default=8000, description="Port number to bind the server")

    # --- WhatsApp / Meta Configuration ---
    whatsapp_phone_number_id: str = Field(
        default="", description="Meta WhatsApp Business Phone Number ID"
    )
    whatsapp_access_token: str = Field(
        default="", description="Permanent or temporary Meta System User access token"
    )
    whatsapp_app_secret: str = Field(
        default="", description="Meta App Secret for HMAC webhook verification"
    )
    whatsapp_webhook_verify_token: str = Field(
        default="", description="Verification token configured in Meta App Dashboard"
    )
    whatsapp_api_version: str = Field(
        default="v20.0", description="Meta Graph API version for WhatsApp Cloud API"
    )

    # --- Azure Storage Configuration ---
    azure_storage_account_name: str = Field(
        default="", description="Azure Blob Storage Account name"
    )
    azure_storage_container_name: str = Field(
        default="documind-documents", description="Container name for original documents"
    )

    # --- Azure AI Search Configuration ---
    azure_search_endpoint: str = Field(
        default="", description="Azure AI Search service endpoint URL"
    )
    azure_search_index_name: str = Field(
        default="documind-index", description="Target index name for vectorized chunks"
    )
    azure_search_api_version: str = Field(
        default="2024-07-01", description="Azure Search REST API version"
    )

    # --- Microsoft Foundry / Azure OpenAI Configuration ---
    azure_openai_endpoint: str = Field(
        default="", description="Azure OpenAI / Microsoft Foundry service endpoint URL"
    )
    azure_openai_api_version: str = Field(
        default="2024-08-01-preview", description="Azure OpenAI API version"
    )
    azure_openai_chat_deployment: str = Field(
        default="", description="Deployment name for chat completion model (e.g., gpt-4o)"
    )
    azure_openai_embedding_deployment: str = Field(
        default="",
        description="Deployment name for embeddings model (e.g., text-embedding-3-small)",
    )
    azure_openai_embedding_dimensions: int = Field(
        default=1536, description="Dimensions for the generated vector embeddings"
    )

    # --- Azure Identity Configuration ---
    azure_client_id: str = Field(
        default="", description="Client ID for Service Principal auth if not using Managed Identity"
    )
    azure_client_secret: str = Field(
        default="", description="Client Secret for Service Principal auth"
    )
    azure_tenant_id: str = Field(
        default="", description="Azure Tenant ID for Service Principal auth"
    )

    # --- Document Processing Configuration ---
    chunk_size: int = Field(
        default=512, description="Target token chunk size for document splitting"
    )
    chunk_overlap: int = Field(default=64, description="Token overlap between consecutive chunks")
    max_file_size_mb: int = Field(
        default=20, description="Maximum permitted file size in Megabytes"
    )
    allowed_extensions: list[str] = Field(
        default=["pdf", "docx", "txt"],
        description="Allowed document file extensions for ingestion",
    )
    document_retention_hours: int = Field(
        default=24,
        description="Maximum retention time in hours for indexed documents before expiration",
    )

    # --- RAG Configuration ---
    top_k_results: int = Field(
        default=5, description="Number of top relevant chunks to retrieve from AI Search"
    )
    min_relevance_score: float = Field(
        default=0.75, description="Minimum similarity/relevance score threshold"
    )

    @field_validator("allowed_extensions", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v: Any) -> list[str]:
        """Parse comma-separated strings or enforce list of extensions."""
        if isinstance(v, str):
            return [ext.strip().lower().lstrip(".") for ext in v.split(",") if ext.strip()]
        if isinstance(v, list | tuple | set):
            return [str(ext).strip().lower().lstrip(".") for ext in v if str(ext).strip()]
        return ["pdf", "docx", "txt"]

    @property
    def max_file_size_bytes(self) -> int:
        """Calculate maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings."""
    return Settings()
