"""WhatsApp Cloud API client for sending messages and downloading media."""

from typing import Any

import httpx
import structlog
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from documind.config.settings import Settings, get_settings

logger = structlog.get_logger(__name__)

_RETRY_ATTEMPTS = 3
_RETRY_WAIT_MIN_S = 1
_RETRY_WAIT_MAX_S = 10
_RETRY_WAIT_MAX_TYPING_S = 5
_HTTP_TIMEOUT_SEND_S = 15.0
_HTTP_TIMEOUT_TYPING_S = 10.0
_HTTP_TIMEOUT_DOWNLOAD_S = 20.0


class WhatsAppError(Exception):
    """Base exception for WhatsApp client operations."""


class WhatsAppAPIError(WhatsAppError):
    """Raised when the WhatsApp Graph API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None, response_body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class MediaDownloadError(WhatsAppError):
    """Raised when downloading media from WhatsApp fails."""


class WhatsAppClient:
    """Async client interacting with the Meta WhatsApp Cloud API."""

    def __init__(
        self,
        settings: Settings | None = None,
        base_url: str | None = None,
        access_token: str | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._api_version = self.settings.whatsapp_api_version
        self._base_url = (
            base_url
            or f"https://graph.facebook.com/{self._api_version}/{self.settings.whatsapp_phone_number_id}"
        )
        token = access_token or self.settings.whatsapp_access_token
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "DocuMindAI/0.1.0",
        }
        self._auth_header = {"Authorization": f"Bearer {token}"}

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=_RETRY_WAIT_MIN_S, max=_RETRY_WAIT_MAX_S),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def send_text_message(self, to: str, body: str) -> dict[str, Any]:
        """Send a standard text message to a WhatsApp user."""
        endpoint = f"{self._base_url}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": body},
        }

        log = logger.bind(recipient=to, length=len(body))
        log.info("Sending WhatsApp text message")

        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT_SEND_S) as client:
            response = await client.post(endpoint, json=payload, headers=self._headers)
            if response.is_error:
                log.error(
                    "WhatsApp API error sending message",
                    status_code=response.status_code,
                    body=response.text,
                )
                raise WhatsAppAPIError(
                    f"Failed to send text message: {response.text}",
                    status_code=response.status_code,
                    response_body=response.text,
                )
            data: dict[str, Any] = response.json()
            log.info("WhatsApp text message delivered successfully", response=data)
            return data

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=_RETRY_WAIT_MIN_S, max=_RETRY_WAIT_MAX_TYPING_S),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def send_typing_indicator(self, to: str, message_id: str | None = None) -> dict[str, Any]:
        """Acknowledge message or mark as read to signal processing."""
        log = logger.bind(recipient=to, message_id=message_id)
        if message_id:
            endpoint = f"{self._base_url}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
            }
            async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT_TYPING_S) as client:
                response = await client.post(endpoint, json=payload, headers=self._headers)
                if not response.is_error:
                    log.info("Marked message as read")
                    return dict(response.json())

        log.info("Typing indicator / processing signal dispatched")
        return {"status": "indicator_sent"}

    @retry(
        stop=stop_after_attempt(_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=_RETRY_WAIT_MIN_S, max=_RETRY_WAIT_MAX_S),
        retry=retry_if_exception_type((httpx.RequestError, MediaDownloadError)),
        reraise=True,
    )
    async def download_media(self, media_id: str) -> bytes:
        """Download binary media from WhatsApp servers using the media ID."""
        log = logger.bind(media_id=media_id)
        log.info("Fetching media metadata URL from WhatsApp")

        metadata_url = f"https://graph.facebook.com/{self._api_version}/{media_id}"
        async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT_DOWNLOAD_S) as client:
            meta_res = await client.get(metadata_url, headers=self._headers)
            if meta_res.is_error:
                log.error(
                    "Failed to get media URL",
                    status_code=meta_res.status_code,
                    body=meta_res.text,
                )
                raise MediaDownloadError(
                    f"Could not retrieve media URL for {media_id}: {meta_res.text}"
                )

            media_data = meta_res.json()
            download_url = media_data.get("url")
            if not download_url:
                raise MediaDownloadError(f"No download URL returned for media ID {media_id}")

            log.info("Downloading binary media bytes", download_url=download_url)

            download_res = await client.get(download_url, headers=self._auth_header)
            if download_res.is_error:
                log.error("Failed to download media file", status_code=download_res.status_code)
                raise MediaDownloadError(
                    f"Failed to download media bytes: {download_res.status_code}"
                )

            log.info("Media downloaded successfully", bytes_count=len(download_res.content))
            return download_res.content
