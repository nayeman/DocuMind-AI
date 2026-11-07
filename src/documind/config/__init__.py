"""Configuration module for DocuMind AI."""

from documind.config.logging import configure_logging
from documind.config.settings import Settings, get_settings

__all__ = ["Settings", "configure_logging", "get_settings"]
