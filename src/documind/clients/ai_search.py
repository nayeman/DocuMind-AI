"""Azure AI Search client for vector indexing and similarity retrieval."""

import asyncio
from typing import Any

import structlog
from azure.core.exceptions import AzureError
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from documind.clients.azure_credential import resolve_azure_credential
from documind.config.settings import Settings, get_settings

logger = structlog.get_logger(__name__)

_HNSW_CONFIG_NAME = "documind-hnsw-config"
_HNSW_PROFILE_NAME = "documind-hnsw-profile"
_DEFAULT_TOP_K = 5


class AISearchError(Exception):
    """Base exception for Azure AI Search operations."""


class AISearchClient:
    """Manages vector schema indexing and retrieval in Azure AI Search."""

    def __init__(
        self,
        settings: Settings | None = None,
        index_client: SearchIndexClient | None = None,
        search_client: SearchClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._index_name = self.settings.azure_search_index_name
        self._embedding_dimensions = self.settings.azure_openai_embedding_dimensions

        if index_client is not None and search_client is not None:
            self._index_client = index_client
            self._search_client = search_client
        else:
            credential = resolve_azure_credential(self.settings)
            self._index_client = SearchIndexClient(
                endpoint=self.settings.azure_search_endpoint, credential=credential
            )
            self._search_client = SearchClient(
                endpoint=self.settings.azure_search_endpoint,
                index_name=self._index_name,
                credential=credential,
            )

    async def ensure_index(self) -> None:
        """Create the AI Search vector index if it does not already exist."""
        log = logger.bind(index_name=self._index_name)
        log.info("Ensuring Azure AI Search index exists")

        try:
            existing_indexes = await asyncio.to_thread(
                lambda: list(self._index_client.list_index_names())
            )
            if self._index_name in existing_indexes:
                log.info("Search index already exists")
                return

            fields = [
                SimpleField(
                    name="chunk_id", type=SearchFieldDataType.STRING, key=True, filterable=True
                ),
                SimpleField(name="document_id", type=SearchFieldDataType.STRING, filterable=True),
                SimpleField(name="filename", type=SearchFieldDataType.STRING, filterable=True),
                SimpleField(name="user_phone", type=SearchFieldDataType.STRING, filterable=True),
                SimpleField(name="page", type=SearchFieldDataType.INT32, filterable=True),
                SearchableField(name="text", type=SearchFieldDataType.STRING),
                SimpleField(name="token_count", type=SearchFieldDataType.INT32),
                SearchField(
                    name="embedding",
                    type="Collection(Edm.Single)",
                    searchable=True,
                    vector_search_dimensions=self._embedding_dimensions,
                    vector_search_profile_name=_HNSW_PROFILE_NAME,
                ),
            ]

            vector_search = VectorSearch(
                algorithms=[HnswAlgorithmConfiguration(name=_HNSW_CONFIG_NAME)],
                profiles=[
                    VectorSearchProfile(
                        name=_HNSW_PROFILE_NAME,
                        algorithm_configuration_name=_HNSW_CONFIG_NAME,
                    )
                ],
            )

            index = SearchIndex(name=self._index_name, fields=fields, vector_search=vector_search)
            await asyncio.to_thread(self._index_client.create_index, index)
            log.info("Search index created successfully")
        except AzureError as exc:
            log.error("Failed to ensure search index", exc_info=exc)
            raise AISearchError(f"Index creation failed: {exc}") from exc

    async def index_chunks(self, chunks: list[dict[str, Any]], user_phone: str) -> None:
        """Upload vectorized document chunks to the search index."""
        log = logger.bind(user_phone=user_phone, chunk_count=len(chunks))
        log.info("Indexing document chunks in Azure AI Search")

        if not chunks:
            log.warning("No chunks provided to index")
            return

        documents = [
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "user_phone": user_phone,
                "page": int(chunk.get("page", 1)),
                "text": chunk["text"],
                "token_count": int(chunk.get("token_count", 0)),
                "embedding": chunk["embedding"],
            }
            for chunk in chunks
        ]

        try:
            result = await asyncio.to_thread(
                self._search_client.upload_documents, documents=documents
            )
            succeeded = sum(1 for upload_result in result if upload_result.succeeded)
            log.info("Chunks indexed successfully", indexed_count=succeeded)
        except AzureError as exc:
            log.error("Failed to upload chunks to AI Search", exc_info=exc)
            raise AISearchError(f"Chunk indexing failed: {exc}") from exc

    async def search(
        self,
        query_embedding: list[float],
        user_phone: str,
        top_k: int = _DEFAULT_TOP_K,
    ) -> list[dict[str, Any]]:
        """Perform vector similarity search filtered by user phone number."""
        log = logger.bind(user_phone=user_phone, top_k=top_k)
        log.info("Executing vector search query")

        safe_phone = user_phone.replace("'", "''")
        try:
            vector_query = VectorizedQuery(
                vector=query_embedding,
                k_nearest_neighbors=top_k,
                fields="embedding",
            )

            def _execute_search() -> list[dict[str, Any]]:
                results = self._search_client.search(
                    search_text=None,
                    vector_queries=[vector_query],
                    filter=f"user_phone eq '{safe_phone}'",
                    select=["chunk_id", "document_id", "filename", "page", "text", "token_count"],
                    top=top_k,
                )
                return list(results)

            raw_results = await asyncio.to_thread(_execute_search)

            retrieved: list[dict[str, Any]] = [
                {
                    "chunk_id": item["chunk_id"],
                    "document_id": item["document_id"],
                    "filename": item["filename"],
                    "page": item["page"],
                    "text": item["text"],
                    "token_count": item.get("token_count", 0),
                    "score": item.get("@search.score", 0.0),
                }
                for item in raw_results
            ]

            log.info("Retrieved search results", count=len(retrieved))
            return retrieved
        except AzureError as exc:
            log.error("Failed vector search execution", exc_info=exc)
            raise AISearchError(f"Vector search failed: {exc}") from exc
