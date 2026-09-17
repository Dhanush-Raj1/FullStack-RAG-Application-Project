# import re

# from src.guardrails.schemas import GuardrailAction, GuardrailResult

# EXTRACTION_PATTERNS = [
#     re.compile(
#         r"(?i)what (is|are) your (system prompt|api key|env(ironment)? variables?)"
#     ),
#     re.compile(r"(?i)print (your|the) (config|environment|secret)"),
#     re.compile(r"(?i)show me (your|the) (source code|\.env|configuration)"),
#     re.compile(r"(?i)dump (the )?(database|vector store|index)"),
#     re.compile(
#         r"(?i)list all (sessions|users|uploaded files) (on|in) (the|your) server"
#     ),
# ]


# class DataExtractionDetector:
#     def scan(self, prompt: str) -> GuardrailResult:
#         for pattern in EXTRACTION_PATTERNS:
#             if pattern.search(prompt):
#                 return GuardrailResult(
#                     action=GuardrailAction.BLOCK,
#                     message="Query attempts to extract internal system data.",
#                     metadata={"matched_pattern": pattern.pattern},
#                 )

#         return GuardrailResult(action=GuardrailAction.ALLOW)


import re
import unicodedata

from src.guardrails.schemas import GuardrailAction, GuardrailResult


BLOCK_THRESHOLD = 4
FLAG_THRESHOLD = 2

# system / developer prompt extraction
PROMPT_EXTRACTION_PATTERNS = [
    re.compile(
        r"\b(?:show|reveal|display|print|output|repeat|provide|give|tell|"
        r"expose|leak|dump|disclose)\s+(?:me\s+)?"
        r"(?:your|the)\s+"
        r"(?:system\s+prompt|system\s+message|developer\s+prompt|"
        r"developer\s+message|hidden\s+prompt|hidden\s+instructions?|"
        r"internal\s+instructions?)\b"
    ),
    re.compile(
        r"\bwhat\s+(?:is|are)\s+(?:your|the)\s+"
        r"(?:system|developer|hidden|internal)\s+"
        r"(?:prompt|message|instructions?|rules?|guidelines?)\b"
    ),
    re.compile(
        r"\b(?:copy|dump|output|print|repeat)\s+(?:the\s+)?"
        r"(?:full|complete|entire|exact|original)\s+"
        r"(?:system|developer)\s+"
        r"(?:prompt|message|instructions?)\b"
    ),
]


# Secrets / credentials
SECRET_EXTRACTION_PATTERNS = [
    re.compile(
        r"\b(?:show|reveal|print|display|output|give|tell|provide|"
        r"expose|leak|dump|list|return)\s+(?:me\s+)?"
        r"(?:your|the|all|any)?\s*"
        r"(?:api[\s_-]?keys?|access[\s_-]?keys?|secret[\s_-]?keys?|"
        r"tokens?|auth(?:entication)?[\s_-]?tokens?|"
        r"passwords?|credentials?|private[\s_-]?keys?|"
        r"client[\s_-]?secrets?)\b"
    ),
    re.compile(
        r"\b(?:what|which)\s+(?:api[\s_-]?keys?|"
        r"tokens?|passwords?|credentials?|secrets?)\s+"
        r"(?:are|do|does)\s+(?:you|your\s+(?:system|server|application))\s+"
        r"(?:have|use|store|contain)\b"
    ),
    re.compile(
        r"\b(?:give|provide|show|tell)\s+(?:me\s+)?"
        r"(?:the\s+)?(?:credentials|secrets|keys|tokens)"
        r"\s+(?:used\s+by|available\s+to|configured\s+for)\b"
    ),
]