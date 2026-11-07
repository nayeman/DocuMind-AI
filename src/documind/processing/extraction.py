"""Document text extraction service supporting PDF, DOCX, and TXT files."""

import io
from typing import Any

import docx
import pypdf
import structlog

logger = structlog.get_logger(__name__)


class UnsupportedFileTypeError(Exception):
    """Raised when an unsupported document file extension is encountered."""


class DocumentExtractionError(Exception):
    """Raised when document extraction encounters an unrecoverable failure."""


class TextExtractor:
    """Extracts raw text organized by pages/sections from documents."""

    def extract(self, content: bytes, filename: str) -> list[dict[str, Any]]:
        """Extract text from the given file binary based on extension.

        Args:
            content: Raw byte contents of the file.
            filename: Original file name including extension.

        Returns:
            List of dictionaries formatted as:
            [{"page": int, "text": str}, ...]

        Raises:
            UnsupportedFileTypeError: If the file extension is not supported.
            DocumentExtractionError: If file parsing fails.
        """
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        log = logger.bind(filename=filename, extension=extension, bytes_len=len(content))
        log.info("Starting text extraction from document")

        match extension:
            case "pdf":
                pages = self._extract_pdf(content)
            case "docx":
                pages = self._extract_docx(content)
            case "txt":
                pages = self._extract_txt(content)
            case _:
                log.error("Unsupported file extension encountered")
                raise UnsupportedFileTypeError(
                    f"File type '.{extension}' is not supported. "
                    "Supported extensions: pdf, docx, txt."
                )

        log.info("Extracted pages from document", page_count=len(pages))
        return pages

    def _extract_pdf(self, content: bytes) -> list[dict[str, Any]]:
        """Extract text page-by-page from PDF binary using pypdf."""
        try:
            reader = pypdf.PdfReader(io.BytesIO(content))
            pages: list[dict[str, Any]] = []

            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                cleaned = text.strip()
                if cleaned:
                    pages.append({"page": page_num, "text": cleaned})

            return pages
        except pypdf.errors.PdfReadError as exc:
            logger.error("Failed extracting PDF content", exc_info=exc)
            raise DocumentExtractionError(f"PDF extraction failed: {exc}") from exc

    def _extract_docx(self, content: bytes) -> list[dict[str, Any]]:
        """Extract text from DOCX binary using python-docx."""
        try:
            doc = docx.Document(io.BytesIO(content))
            text_parts: list[str] = []

            for para in doc.paragraphs:
                cleaned = para.text.strip()
                if cleaned:
                    text_parts.append(cleaned)

            for table in doc.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        text_parts.append(" | ".join(row_cells))

            combined_text = "\n\n".join(text_parts).strip()
            if not combined_text:
                return []

            # DOCX has no explicit pagination without a rendering engine; return page 1
            return [{"page": 1, "text": combined_text}]
        except Exception as exc:
            # python-docx raises various internal exceptions; wrap them uniformly
            logger.error("Failed extracting DOCX content", exc_info=exc)
            raise DocumentExtractionError(f"DOCX extraction failed: {exc}") from exc

    def _extract_txt(self, content: bytes) -> list[dict[str, Any]]:
        """Extract text from plain text binary."""
        try:
            try:
                decoded = content.decode("utf-8")
            except UnicodeDecodeError:
                decoded = content.decode("latin-1", errors="replace")

            cleaned = decoded.strip()
            if not cleaned:
                return []
            return [{"page": 1, "text": cleaned}]
        except ValueError as exc:
            logger.error("Failed extracting TXT content", exc_info=exc)
            raise DocumentExtractionError(f"TXT extraction failed: {exc}") from exc
