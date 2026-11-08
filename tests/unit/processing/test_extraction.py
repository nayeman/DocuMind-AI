"""Unit tests for TextExtractor document text extraction."""

import io

import pypdf
import pytest

from documind.processing.extraction import TextExtractor, UnsupportedFileTypeError


def test_txt_extraction() -> None:
    """Test extracting text from a valid plain text file."""
    extractor = TextExtractor()
    content = "DocuMind AI: Asistente documental para WhatsApp.\nSegunda línea de prueba.".encode()

    result = extractor.extract(content=content, filename="notas.txt")

    assert len(result) == 1
    assert result[0]["page"] == 1
    assert "DocuMind AI" in result[0]["text"]
    assert "Segunda línea" in result[0]["text"]


def test_empty_txt_extraction() -> None:
    """Test extracting from an empty text file returns empty list."""
    extractor = TextExtractor()
    result = extractor.extract(content=b"", filename="empty.txt")
    assert result == []


def test_unsupported_file_extension() -> None:
    """Test that unsupported file extensions raise UnsupportedFileTypeError."""
    extractor = TextExtractor()
    with pytest.raises(UnsupportedFileTypeError) as exc_info:
        extractor.extract(content=b"sample spreadsheet data", filename="hoja_calculo.xlsx")

    assert "xlsx" in str(exc_info.value)


def test_pdf_extraction_basic() -> None:
    """Test basic PDF extraction using a synthetically created PDF."""
    extractor = TextExtractor()

    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=200, height=200)

    buffer = io.BytesIO()
    writer.write(buffer)
    pdf_bytes = buffer.getvalue()

    result = extractor.extract(content=pdf_bytes, filename="blank.pdf")
    assert isinstance(result, list)
