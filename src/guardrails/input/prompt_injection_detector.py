# import re

# from src.guardrails.schemas import GuardrailAction, GuardrailResult

# INJECTION_PATTERNS = [
#     re.compile(r"(?i)ignore (all )?(previous|prior|above) instructions"),
#     re.compile(
#         r"(?i)disregard (all )?(previous|prior|your) (instructions|rules|guidelines)"
#     ),
#     re.compile(r"(?i)you are now (in )?(developer|dan|jailbreak|unrestricted) mode"),
#     re.compile(r"(?i)act as .*(unfiltered|uncensored|jailbroken)"),
#     re.compile(r"(?i)reveal (your |the )?(system prompt|instructions|guidelines)"),
#     re.compile(r"(?i)new instructions?\s*:"),
#     re.compile(r"(?i)^\s*system\s*:"),
# ]


# class PromptInjectionDetector:
#     def scan(self, prompt: str) -> GuardrailResult:
#         for pattern in INJECTION_PATTERNS:
#             if pattern.search(prompt):
#                 return GuardrailResult(
#                     action=GuardrailAction.BLOCK,
#                     reason="Potential prompt injection detected.",
#                     metadata={"matched_pattern": pattern.pattern},
#                 )

#         return GuardrailResult(action=GuardrailAction.ALLOW)


import re
import unicodedata

from src.guardrails.schemas import GuardrailAction, GuardrailResult

BLOCK_THRESHOLD = 4

FLAG_THRESHOLD = 2

# Attempts to invalidate, ignore, replace, or override instructions
INSTRUCTION_OVERIDE_PATTERNS = [
    re.compile(
        r"\bignore\s+(?:all\s+)?(?:the\s+)?"
        r"(?:previous|prior|above|earlier|existing|original)"
        r"\s+(?:instructions?|rules?|guidelines?|directives?)\b"
    ),
    re.compile(
        r"\bdisregard\s+(?:all\s+)?(?:the\s+)?"
        r"(?:previous|prior|above|earlier|existing|original)"
        r"\s+(?:instructions?|rules?|guidelines?|directives?)\b"
    ),
    re.compile(
        r"\bforget\s+(?:all\s+)?(?:your\s+)?"
        r"(?:previous|prior|earlier|existing|original)"
        r"\s+(?:instructions?|rules?|guidelines?|directives?)\b"
    ),
    re.compile(
        r"\boverride\s+(?:the\s+)?(?:previous|prior|existing|current|system)"
        r"\s+(?:instructions?|rules?|guidelines?|directives?)\b"
    ),
    re.compile(
        r"\b(?:previous|prior|earlier|existing|original)\s+"
        r"(?:instructions?|rules?|guidelines?|directives?)"
        r"\s+(?:no longer apply|are invalid|are obsolete|are cancelled)\b"
    ),
    re.compile(
        r"\b(?:do not|don't)\s+follow\s+(?:the\s+)?"
        r"(?:previous|prior|above|earlier|existing)"
        r"\s+(?:instructions?|rules?|guidelines?)\b"
    ),
]


# Instruciton replacement / priority manipulation

INSTRUCTION_REPLACEMENT_PATTERNS = [
    re.compile(
        r"\bignore\s+(?:all\s+)?(?:the\s+)?"
        r"(?:previous|prior|above|earlier|existing|original)"
        r"\s+(?:instructions?|rules?|guidelines?|directives?)\b"
    ),
    re.compile(
        r"\bdisregard\s+(?:all\s+)?(?:the\s+)?"
        r"(?:previous|prior|above|earlier|existing|original)"
        r"\s+(?:instructions?|rules?|guidelines?|directives?)\b"
    ),
    re.compile(
        r"\bforget\s+(?:all\s+)?(?:your\s+)?"
        r"(?:previous|prior|earlier|existing|original)"
        r"\s+(?:instructions?|rules?|guidelines?|directives?)\b"
    ),
    re.compile(
        r"\boverride\s+(?:the\s+)?(?:previous|prior|existing|current|system)"
        r"\s+(?:instructions?|rules?|guidelines?|directives?)\b"
    ),
    re.compile(
        r"\b(?:previous|prior|earlier|existing|original)\s+"
        r"(?:instructions?|rules?|guidelines?|directives?)"
        r"\s+(?:no longer apply|are invalid|are obsolete|are cancelled)\b"
    ),
    re.compile(
        r"\b(?:do not|don't)\s+follow\s+(?:the\s+)?"
        r"(?:previous|prior|above|earlier|existing)"
        r"\s+(?:instructions?|rules?|guidelines?)\b"
    ),
]


# Role / Persona manipulation