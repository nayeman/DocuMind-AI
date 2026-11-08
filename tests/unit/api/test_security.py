"""Unit tests for Meta WhatsApp HMAC-SHA256 webhook signature verification."""

import hashlib
import hmac

from documind.api.security import verify_meta_signature


def test_verify_meta_signature_valid() -> None:
    """Verify that a valid HMAC-SHA256 signature returns True."""
    secret = "my_meta_secret_key"
    body = b'{"object": "whatsapp_business_account"}'
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    assert verify_meta_signature(raw_body=body, signature_header=signature, secret=secret) is True


def test_verify_meta_signature_invalid_hash() -> None:
    """Verify that a tampered signature returns False."""
    secret = "my_meta_secret_key"
    body = b'{"object": "whatsapp_business_account"}'
    invalid_signature = "sha256=abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"

    assert (
        verify_meta_signature(raw_body=body, signature_header=invalid_signature, secret=secret)
        is False
    )


def test_verify_meta_signature_missing_or_bad_prefix() -> None:
    """Verify that missing or malformed signature header returns False."""
    secret = "my_meta_secret_key"
    body = b'{"object": "whatsapp_business_account"}'

    assert verify_meta_signature(raw_body=body, signature_header=None, secret=secret) is False
    assert (
        verify_meta_signature(raw_body=body, signature_header="invalidprefix", secret=secret)
        is False
    )
