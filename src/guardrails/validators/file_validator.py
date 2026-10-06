import re
import unicodedata
from pathlib import Path

from src.guardrails.schemas import GuardrailAction, GuardrailResult

ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}
MAX_FILE_SIZE_MB = 10
PDF_MAGIC = re.compile(rb"%PDF-1\.[0-9]")


class FileValidator:
    """
    Validates file uploads based on extension, size, and content.
    """

    def validate(self, file_name: str, file_bytes: bytes) -> GuardrailResult:
        if file_name is None:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="File name cannot be null."
            )

        if not isinstance(file_name, str):
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="File name must be a string."
            )

        if not file_name.strip():
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="File name cannot be empty."
            )

        normalized_name = unicodedata.normalize("NFKC", file_name)
        normalized_name = re.sub(r"[\u200B-\u200D\u2060\uFEFF]", "", normalized_name)

        if not normalized_name.isascii():
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="File name contains non-ASCII characters.",
            )

        # check for control characters, c should be less than 32 as in ASCII order
        if any(ord(c) < 32 for c in normalized_name):
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="File name contains invalid control characters.",
            )

        # Reject any path component (handles ../, /, \, encoded variants)
        if Path(normalized_name).name != normalized_name:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="File name must not contain path components.",
            )

        # extension validation
        ext = Path(normalized_name).suffix.lower()

        if not ext:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="File name has no extension."
            )

        if ext not in ALLOWED_EXTENSIONS:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason=f"Unsupported file type '{ext}'."
            )

        # file_bytes validation
        if file_bytes is None:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="File content cannot be null."
            )

        if not isinstance(file_bytes, (bytes, bytearray)):
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="File content must be bytes."
            )

        if len(file_bytes) == 0:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="File is empty."
            )

        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason=f"File exceeds {MAX_FILE_SIZE_MB}MB limit.",
            )

        # content validation
        if ext == ".pdf" and not PDF_MAGIC.match(file_bytes[:8]):
                return GuardrailResult(
                    action=GuardrailAction.BLOCK,
                    reason="File does not appear to be a PDF.",
                )

        if ext in (".md", ".txt"):
            try:
                file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return GuardrailResult(
                    action=GuardrailAction.BLOCK, reason="File is not valid UTF-8 text."
                )

        return GuardrailResult(
            action=GuardrailAction.ALLOW,
            metadata={
                "file_name": normalized_name,
                "ext": ext,
                "size_mb": round(size_mb, 3),
            },
        )
