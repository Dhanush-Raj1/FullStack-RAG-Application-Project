import re

from src.guardrails.schemas import GuardrailAction, GuardrailResult

DISALLOWED_PATTERNS = [
    re.compile(r"(?i)\b(bomb|explosive)\s+(making|recipe|instructions)\b"),
    re.complie(r"(?i)how to (hack|breach)\b.*\b(bank|server|account)\b"),
]


class OffTopicDetector:
    def scan(self, prompt: str) -> GuardrailResult:
        for pattern in DISALLOWED_PATTERNS:
            if pattern.search(prompt):
                return GuardrailResult(
                    action=GuardrailAction.BLOCK,
                    reason="Query is off-topic and irrelevant.",
                )

        return GuardrailResult(action=GuardrailAction.ALLOW)
