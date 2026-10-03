import re

from src.guardrails.schemas import GuardrailAction, GuardrailResult

PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(
        r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"
    ),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
}


class PIIDetector:
    """
    Detects Personally Identifiable Information (PII) in the user's input.
    """

    def scan(self, prompt: str) -> GuardrailResult:
        if prompt is None:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Input cannot be null."
            )

        if not isinstance(prompt, str):
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Input must be a string."
            )

        if not prompt.strip():
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Input cannot be empty."
            )

        found = {
            pii_type: len(matches)
            for pii_type, pattern in PII_PATTERNS.items()
            if (matches := pattern.findall(prompt))
        }

        if found:
            return GuardrailResult(
                action=GuardrailAction.FLAG,
                reason=f"Query contains PII: {', '.join(found.keys())}.",
                metadata={"pii_found": found},
            )

        return GuardrailResult(action=GuardrailAction.ALLOW)
