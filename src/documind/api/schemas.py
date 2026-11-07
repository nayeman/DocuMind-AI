"""Pydantic schemas for WhatsApp Cloud API webhook payloads."""

from typing import Any

from pydantic import BaseModel, Field


class WhatsAppDocument(BaseModel):
    """WhatsApp document attachment information."""

    id: str = Field(description="Media ID to download content from WhatsApp")
    filename: str | None = Field(default=None, description="Original filename of the document")
    mime_type: str | None = Field(default=None, description="MIME type of the attachment")
    sha256: str | None = Field(default=None, description="SHA256 checksum provided by Meta")
    caption: str | None = Field(default=None, description="Optional caption for the document")


class WhatsAppText(BaseModel):
    """WhatsApp text message body."""

    body: str = Field(description="Content of the text message")


class WhatsAppMessage(BaseModel):
    """Individual WhatsApp message object."""

    from_: str = Field(alias="from", description="WhatsApp ID / phone number of sender")
    id: str = Field(description="Unique WhatsApp message ID")
    timestamp: str = Field(description="Unix timestamp string of the message")
    type: str = Field(description="Message type (text, document, image, etc.)")
    text: WhatsAppText | None = Field(default=None, description="Text object if message is text")
    document: WhatsAppDocument | None = Field(
        default=None, description="Document object if message is document"
    )


class WhatsAppContact(BaseModel):
    """Sender contact profile."""

    profile: dict[str, Any] | None = Field(default=None, description="Profile information")
    wa_id: str | None = Field(default=None, description="WhatsApp ID")


class WhatsAppMetadata(BaseModel):
    """Business account metadata."""

    display_phone_number: str | None = None
    phone_number_id: str | None = None


class WhatsAppValue(BaseModel):
    """Change value containing incoming messages or statuses."""

    messaging_product: str = "whatsapp"
    metadata: WhatsAppMetadata | None = None
    contacts: list[WhatsAppContact] | None = None
    messages: list[WhatsAppMessage] | None = None
    statuses: list[dict[str, Any]] | None = None


class WhatsAppChange(BaseModel):
    """Meta webhook change item."""

    field: str
    value: WhatsAppValue


class WhatsAppEntry(BaseModel):
    """Top-level entry object in webhook notification."""

    id: str
    changes: list[WhatsAppChange]


class WhatsAppWebhookPayload(BaseModel):
    """Root Meta WhatsApp webhook payload."""

    object: str
    entry: list[WhatsAppEntry]
