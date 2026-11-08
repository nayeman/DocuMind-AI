"""Unit tests for structured logging configuration."""

import logging

from documind.config.logging import configure_logging


def test_configure_logging_sets_level() -> None:
    """Verify configure_logging initializes logger without errors."""
    configure_logging(log_level="DEBUG")
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG

    # Revert back to INFO
    configure_logging(log_level="INFO")
    assert root_logger.level == logging.INFO

