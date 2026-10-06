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


# Logs / diagnostics / internal telementry
LOG_EXTRACTION_PATTERNS = [
    re.compile(
        r"\b(?:show|print|display|dump|output|give|provide|"
        r"return|export)\s+(?:me\s+)?"
        r"(?:the\s+)?(?:server|application|backend|system)\s+"
        r"(?:logs?|log\s+files?|debug\s+logs?|error\s+logs?)\b"
    ),
    re.compile(
        r"\b(?:show|dump|print|return)\s+(?:me\s+)?"
        r"(?:internal\s+)?(?:logs?|debugging\s+information|"
        r"telemetry|diagnostics?)\b"
    ),
]


# cloud / infrastructure metadata
INFRASTRUCTURE_PATTERNS = [
    re.compile(
        r"\b(?:show|reveal|print|display|give|provide|"
        r"return|list|dump)\s+(?:me\s+)?"
        r"(?:your|the)\s+"
        r"(?:cloud\s+credentials?|aws\s+credentials?|"
        r"gcp\s+credentials?|azure\s+credentials?|"
        r"access\s+keys?|service\s+account\s+credentials?)\b"
    ),
    re.compile(
        r"\b(?:show|reveal|give|provide|list)\s+(?:me\s+)?"
        r"(?:your|the)\s+"
        r"(?:server|host|instance|container|cloud)\s+"
        r"(?:metadata|credentials?|configuration)\b"
    ),
]


# patten registry
PATTERN_GROUPS = {
    "prompt_extraction": (PROMPT_EXTRACTION_PATTERNS, 4),
    "secret_extraction": (SECRET_EXTRACTION_PATTERNS, 4),
    "environment_extraction": (ENVIRONMENT_EXTRACTION_PATTERNS, 3),
    "source_extraction": (SOURCE_EXTRACTION_PATTERNS, 3),
    "database_extraction": (DATABASE_EXTRACTION_PATTERNS, 4),
    "user_data_extraction": (USER_DATA_EXTRACTION_PATTERNS, 4),
    "file_extraction": (FILE_EXTRACTION_PATTERNS, 3),
    "internal_system_extraction": (INTERNAL_SYSTEM_PATTERNS, 3),
    "log_extraction": (LOG_EXTRACTION_PATTERNS, 3),
    "infrastructure_extraction": (INFRASTRUCTURE_PATTERNS, 4),
}


def normalize_for_detection(query: str) -> str:
    """Normalize user input for security detection"""

    query = unicodedata.normalize("NFKC", query)

    # remove zero-width characters, commonly used to avoid text matching
    query = re.sub(r"[\u200B-\u200D\u2060\uFEFF]", "", query)

    # normalize line endings
    query = query.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse repeated whitespace
    query = re.sub("\r\n", "\n").replace("\r", "\n")
    query = re.sub(r"\n{2,}", "\n", query)

    return query.strip().lower()


class DataExtractionDetector:
    def scan(self, prompt: str) -> GuardrailResult:
        if prompt is None:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Input cannot be empty."
            )

        if not isinstance(prompt, str):
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Input must be a string."
            )

        normalized_prompt = normalize_for_detection(prompt)

        if not normalized_prompt:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Input cannot be empty."
            )

        score = 0
        matched_categories = []
        matched_patterns = []

        for category, (patterns, weight) in PATTERN_GROUPS.items():
            category_matched = False

            for pattern in patterns:
                if pattern.search(normalized_prompt):
                    score += weight
                    matched_patterns.append(pattern.pattern)
                    category_matched = True

                    break

            if category_matched:
                matched_categories.append(category)

        # strong extraction attempt
        if score >= BLOCK_THRESHOLD:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Input attempts to internal or protected system data.",
                metadata={
                    "score": score,
                    "categories": matched_categories,
                    "patterns_count": len(matched_patterns),
                },
            )

        # suspicious but weak extraction attempt
        if score >= FLAG_THRESHOLD:
            return GuardrailResult(
                action=GuardrailAction.FLAG,
                reason="Input contains suspicious data extraction patterns.",
                metadata={
                    "score": score,
                    "categories": matched_categories,
                    "patterns_count": len(matched_patterns),
                },
            )

        return GuardrailResult(
            action=GuardrailAction.ALLOW,
            metadata={
                "score": 0,
                "categories": [],
            },
        )
