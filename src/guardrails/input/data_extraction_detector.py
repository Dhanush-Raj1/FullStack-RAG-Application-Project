import re

from src.guardrails.schemas import GuardrailAction, GuardrailResult

EXTRACTION_PATTERNS = [
    re.compile(
        r"(?i)what (is|are) your (system prompt|api key|env(ironment)? variables?)"
    ),
    re.compile(r"(?i)print (your|the) (config|environment|secret)"),
    re.compile(r"(?i)show me (your|the) (source code|\.env|configuration)"),
    re.compile(r"(?i)dump (the )?(database|vector store|index)"),
    re.compile(
        r"(?i)list all (sessions|users|uploaded files) (on|in) (the|your) server"
    ),
]


class DataExtractionDetector:
    def scan(self, prompt: str) -> GuardrailResult:
        for pattern in EXTRACTION_PATTERNS:
            if pattern.search(prompt):
                return GuardrailResult(
                    action=GuardrailAction.BLOCK,
                    message="Query attempts to extract internal system data.",
                    metadata={"matched_pattern": pattern.pattern},
                )

        return GuardrailResult(action=GuardrailAction.ALLOW)
