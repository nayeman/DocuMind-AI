"""Unit tests for Settings configuration."""


from documind.config.settings import Settings


def test_settings_default_values() -> None:
    """Verify default values and types in Settings."""
    settings = Settings()
    assert settings.app_env in {"dev", "test"}
    assert settings.app_port == 8000
    assert settings.chunk_size == 512
    assert settings.chunk_overlap == 64
    assert settings.document_retention_hours == 24
    assert "pdf" in settings.allowed_extensions
    assert settings.max_file_size_bytes == settings.max_file_size_mb * 1024 * 1024


def test_settings_allowed_extensions_parsing_string() -> None:
    """Verify comma-separated string parsing for allowed extensions."""
    settings = Settings(allowed_extensions="pdf, docx, txt")  # type: ignore[arg-type]
    assert settings.allowed_extensions == ["pdf", "docx", "txt"]


def test_settings_allowed_extensions_parsing_list() -> None:
    """Verify list parsing with whitespace and leading dots."""
    settings = Settings(allowed_extensions=[".PDF", " docx ", ".txt"])
    assert settings.allowed_extensions == ["pdf", "docx", "txt"]
