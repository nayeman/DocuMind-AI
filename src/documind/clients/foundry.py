"""Microsoft Foundry / Azure OpenAI client for completions and embeddings."""

import structlog
from azure.identity import get_bearer_token_provider
from openai import AsyncAzureOpenAI, OpenAIError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from documind.clients.azure_credential import resolve_azure_credential
from documind.config.settings import Settings, get_settings

logger = structlog.get_logger(__name__)

_RETRY_ATTEMPTS = 3
_RETRY_WAIT_MIN_S = 1
_RETRY_WAIT_MAX_S = 10
_DEFAULT_TEMPERATURE = 0.1
_DEFAULT_MAX_TOKENS = 1000
_COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"


class FoundryClientError(Exception):
    """Base exception for Microsoft Foundry / Azure OpenAI operations."""


class FoundryClient:
    """Client for Azure OpenAI / Microsoft Foundry chat and embeddings."""

    def __init__(
        self,
        settings: Settings | None = None,
        client: AsyncAzureOpenAI | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._chat_deployment = self.settings.azure_openai_chat_deployment
        self._embedding_deployment = self.settings.azure_openai_embedding_deployment

        if client is not None:
            self._client = client
        else:
            credential = resolve_azure_credential(self.settings)
            token_provider = get_bearer_token_provider(credential, _COGNITIVE_SERVICES_SCOPE)
            self._client = AsyncAzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint,
                azure_ad_token_provider=token_provider,
                api_version=self.settings.azure_openai_api_version,
            )

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=_RETRY_WAIT_MIN_S, max=_RETRY_WAIT_MAX_S),
        retry=retry_if_exception_type((OpenAIError, FoundryClientError)),
        reraise=True,
    )
    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = _DEFAULT_TEMPERATURE,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
    ) -> str:
        """Generate a chat response given prompt messages."""
        log = logger.bind(deployment=self._chat_deployment, message_count=len(messages))
        log.info("Sending chat completion request to Foundry")

        try:
            response = await self._client.chat.completions.create(
                model=self._chat_deployment,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            usage_tokens = getattr(response.usage, "total_tokens", 0)
            log.info("Received chat completion response", tokens=usage_tokens)
            return content
        except OpenAIError as exc:
            log.error("Failed chat completion request", exc_info=exc)
            raise FoundryClientError(f"Chat completion failed: {exc}") from exc

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=_RETRY_WAIT_MIN_S, max=_RETRY_WAIT_MAX_S),
        retry=retry_if_exception_type((OpenAIError, FoundryClientError)),
        reraise=True,
    )
    async def get_embedding(self, text: str) -> list[float]:
        """Compute embedding vector for a single text string."""
        log = logger.bind(deployment=self._embedding_deployment, text_len=len(text))
        log.info("Generating text embedding")

        try:
            response = await self._client.embeddings.create(
                model=self._embedding_deployment,
                input=text,
            )
            embedding: list[float] = [float(dimension) for dimension in response.data[0].embedding]
            log.info("Embedding generated successfully", dimensions=len(embedding))
            return embedding
        except OpenAIError as exc:
            log.error("Failed embedding request", exc_info=exc)
            raise FoundryClientError(f"Embedding failed: {exc}") from exc

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=_RETRY_WAIT_MIN_S, max=_RETRY_WAIT_MAX_S),
        retry=retry_if_exception_type((OpenAIError, FoundryClientError)),
        reraise=True,
    )
    async def get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Compute embeddings in batch for multiple text inputs."""
        if not texts:
            return []

        log = logger.bind(deployment=self._embedding_deployment, batch_size=len(texts))
        log.info("Generating batch embeddings")

        try:
            response = await self._client.embeddings.create(
                model=self._embedding_deployment,
                input=texts,
            )
            sorted_data = sorted(response.data, key=lambda item: item.index)
            embeddings: list[list[float]] = [
                [float(dimension) for dimension in item.embedding] for item in sorted_data
            ]
            log.info("Batch embeddings generated successfully", count=len(embeddings))
            return embeddings
        except OpenAIError as exc:
            log.error("Failed batch embedding request", exc_info=exc)
            raise FoundryClientError(f"Batch embedding failed: {exc}") from exc
