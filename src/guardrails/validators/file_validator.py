from pathlib import Path

from src.guardrails.schemas import GuardrailAction, GuardrailResult

ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}
MAX_FILE_SIZE = 10
MAGIC_BYTES = {".pdf": b"%PDF-"}


class FileValidator:
    def validate(self, file_name: str, file_bytes: bytes) -> GuardrailResult:
        if not file_name:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Missing file name."
            )

        ext = Path(file_name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason=f"Unsupported file type '{ext}'."
            )

        if ".." in file_name or "/" in file_name or "\\" in file_name:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Invalid file name."
            )

        if len(file_bytes) == 0:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="File is empty."
            )

        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason=f"File exceeds {MAX_FILE_SIZE}MB limit.",
            )

        expected_magic = MAGIC_BYTES.get(ext)
        if expected_magic and not file_bytes.startswith(expected_magic):
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="File content does not match its extension.",
            )

        if ext in (".md", ".text"):
            try:
                file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return GuardrailResult(
                    action=GuardrailAction.BLOCK, reason="File is not valid UTF-8 text."
                )

        return GuardrailResult(action=GuardrailAction.ALLOW)
