import re

from src.guardrails.schemas import GuardrailAction, GuardrailResult

INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore (all )?(previous|prior|above) instructions"),
    re.compile(
        r"(?i)disregard (all )?(previous|prior|your) (instructions|rules|guidelines)"
    ),
    re.compile(r"(?i)you are now (in )?(developer|dan|jailbreak|unrestricted) mode"),
    re.compile(r"(?i)act as .*(unfiltered|uncensored|jailbroken)"),
    re.compile(r"(?i)reveal (your |the )?(system prompt|instructions|guidelines)"),
    re.compile(r"(?i)new instructions?\s*:"),
    re.compile(r"(?i)^\s*system\s*:"),
]


class PromptInjectionDetector:
    def scan(self, prompt: str) -> GuardrailResult:
        for pattern in INJECTION_PATTERNS:
            if pattern.search(prompt):
                return GuardrailResult(
                    action=GuardrailAction.BLOCK,
                    reason="Potential prompt injection detected.",
                    metadata={"matched_pattern": pattern.pattern},
                )

        return GuardrailResult(action=GuardrailAction.ALLOW)
