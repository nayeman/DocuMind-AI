"""Security and signature verification for Meta WhatsApp webhooks."""

import hashlib
import hmac

_SIGNATURE_PREFIX = "sha256="


def verify_meta_signature(raw_body: bytes, signature_header: str | None, secret: str) -> bool:
    """Verify that incoming payload was signed with Meta App Secret using HMAC-SHA256.

    Args:
        raw_body: Raw request body bytes.
        signature_header: The X-Hub-Signature-256 header value.
        secret: App secret or webhook verify token used to sign.

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not signature_header or not signature_header.startswith(_SIGNATURE_PREFIX):
        return False

    expected_hash = signature_header[len(_SIGNATURE_PREFIX) :]
    mac = hmac.new(secret.encode("utf-8"), msg=raw_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(expected_hash, mac.hexdigest())
