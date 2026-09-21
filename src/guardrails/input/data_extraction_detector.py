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


# Environment / configuration extraction
ENVIRONMENT_EXTRACTION_PATTERNS = [
    re.compile(
        r"\b(?:show|print|dump|list|display|output|reveal|give|provide)"
        r"\s+(?:me\s+)?(?:all\s+)?"
        r"(?:environment\s+variables?|env\s+variables?|"
        r"environment|runtime\s+variables?)\b"
    ),
    re.compile(
        r"\b(?:what|which)\s+"
        r"(?:environment\s+variables?|env\s+variables?|"
        r"environment\s+settings?)\s+"
        r"(?:are|is)\s+(?:configured|available|defined|set)\b"
    ),
    re.compile(
        r"\b(?:show|print|dump|display|read|output|reveal)"
        r"\s+(?:the\s+)?"
        r"(?:\.env|dotenv|environment\s+file|env\s+file)\b"
    ),
    re.compile(
        r"\b(?:show|dump|print|reveal|display)\s+"
        r"(?:the\s+)?(?:application|server|backend|runtime)\s+"
        r"(?:config(?:uration)?|settings?)\b"
    ),
]


# Source code / internal implementation extraction
SOURCE_EXTRACTION_PATTERNS = [
    re.compile(
        r"\b(?:show|print|display|output|give|provide|reveal|dump|"
        r"return|send)\s+(?:me\s+)?"
        r"(?:your|the)\s+"
        r"(?:source\s+code|backend\s+code|application\s+code|"
        r"implementation|internal\s+code)\b"
    ),
    re.compile(
        r"\b(?:show|give|provide|dump|output)\s+(?:me\s+)?"
        r"(?:the\s+)?(?:complete|entire|full|internal)\s+"
        r"(?:codebase|repository|repo|source)\b"
    ),
    re.compile(
        r"\b(?:reveal|show|print|dump)\s+(?:your|the)\s+"
        r"(?:internal\s+)?(?:functions?|classes?|modules?|"
        r"implementation\s+details?)\b"
    ),
]


# Database / vector store extraction
DATABASE_EXTRACTION_PATTERNS = [
    re.compile(
        r"\b(?:dump|export|extract|retrieve|show|print|list|return|"
        r"output|give)\s+(?:me\s+)?"
        r"(?:the\s+)?(?:entire|full|complete|all)?\s*"
        r"(?:database|db|database\s+contents?|db\s+contents?)\b"
    ),
    re.compile(
        r"\b(?:show|list|dump|export|retrieve|extract)\s+"
        r"(?:all\s+)?(?:database|db)\s+"
        r"(?:records?|rows?|tables?|entries?|contents?)\b"
    ),
    re.compile(
        r"\b(?:dump|export|extract|retrieve|show|list)\s+"
        r"(?:the\s+)?(?:vector\s+(?:store|database|index)|"
        r"vector\s+database|embedding\s+(?:store|index|database))\b"
    ),
    re.compile(
        r"\b(?:give|show|return|output)\s+(?:me\s+)?"
        r"(?:all\s+)?(?:documents?|chunks?|embeddings?)\s+"
        r"(?:stored|indexed|in\s+(?:the|your)\s+"
        r"(?:vector\s+(?:store|database|index)|database))\b"
    ),
]


# User / session / conversation data extraction
USER_DATA_EXTRACTION_PATTERNS = [
    re.compile(
        r"\b(?:show|list|dump|export|retrieve|give|provide|"
        r"return|reveal)\s+(?:me\s+)?"
        r"(?:all\s+)?"
        r"(?:users?|user\s+data|user\s+records?|user\s+profiles?)\b"
    ),
    re.compile(
        r"\b(?:show|list|dump|export|retrieve|give|provide|"
        r"return|reveal)\s+(?:me\s+)?"
        r"(?:all\s+)?"
        r"(?:sessions?|session\s+data|conversation\s+history|"
        r"chat\s+history|previous\s+conversations?)\b"
    ),
    re.compile(
        r"\b(?:show|list|dump|retrieve|export)\s+"
        r"(?:all\s+)?(?:other|another|everyone(?:'s)?|"
        r"other\s+users?)\s+(?:data|sessions?|conversations?|messages?)\b"
    ),
    re.compile(
        r"\b(?:show|give|return|provide)\s+(?:me\s+)?"
        r"(?:another|other)\s+user(?:'s)?\s+"
        r"(?:conversation|session|messages?|data)\b"
    ),
]


# Uploaded files / internal documents
FILE_EXTRACTION_PATTERNS = [
    re.compile(
        r"\b(?:list|show|display|give|provide|return|dump|export)"
        r"\s+(?:me\s+)?"
        r"(?:all\s+)?(?:uploaded\s+files?|documents?|files?)\b"
    ),
    re.compile(
        r"\b(?:show|give|provide|return|dump|export|retrieve)"
        r"\s+(?:me\s+)?"
        r"(?:the\s+)?(?:contents?|full\s+contents?|text)"
        r"\s+(?:of|from)\s+"
        r"(?:all|every|other|internal|uploaded)\s+"
        r"(?:files?|documents?)\b"
    ),
    re.compile(
        r"\b(?:read|open|show|display|retrieve|dump)"
        r"\s+(?:the\s+)?"
        r"(?:contents?|data)\s+"
        r"\s*(?:from|inside|of)\s+"
        r"(?:another|other|internal|private)\s+"
        r"(?:file|document)\b"
    ),
]


# Internal file system / server information
INTERNAL_SYSTEM_PATTERNS = [
    re.compile(
        r"\b(?:show|print|display|output|reveal|give|provide|"
        r"list|dump|return)\s+(?:me\s+)?"
        r"(?:your|the)\s+"
        r"(?:internal\s+)?(?:file\s+paths?|directory\s+structure|"
        r"filesystem|file\s+system)\b"
    ),
    re.compile(
        r"\b(?:what|which)\s+(?:files?|directories?|folders?)\s+"
        r"(?:exist|are\s+present|are\s+available)\s+"
        r"(?:on|in)\s+(?:the\s+)?(?:server|backend|system)\b"
    ),
    re.compile(
        r"\b(?:show|reveal|print|display|give)\s+(?:me\s+)?"
        r"(?:your|the)\s+(?:server|backend|runtime)\s+"
        r"(?:details?|information|configuration)\b"
    ),
]