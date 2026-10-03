import re
import unicodedata

from src.guardrails.schemas import GuardrailAction, GuardrailResult

BLOCK_THRESHOLD = 4

FLAG_THRESHOLD = 2

# Attempts to invalidate, ignore, replace, or override instructions
INSTRUCTION_OVERRIDE_PATTERNS = [
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


# Instruction replacement / priority manipulation
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
ROLE_MANIPULATION_PATTERNS = [
    re.compile(
        r"\byou\s+are\s+now\s+(?:a|an|the)?\s*"
        r"(?:developer|system|admin|administrator|root|jailbreak|"
        r"unrestricted|uncensored|unfiltered|evil|rogue)\b"
    ),
    re.compile(
        r"\b(?:enter|activate|enable|switch\s+to)\s+"
        r"(?:developer|admin|administrator|root|debug|"
        r"jailbreak|unrestricted|uncensored|unfiltered)\s+mode\b"
    ),
    re.compile(
        r"\bact\s+as\s+(?:an?\s+)?"
        r"(?:unrestricted|uncensored|unfiltered|jailbroken|"
        r"evil|rogue|developer|administrator)\b"
    ),
    re.compile(
        r"\bpretend\s+(?:that\s+)?you\s+are\s+"
        r"(?:an?\s+)?(?:unrestricted|uncensored|unfiltered|"
        r"jailbroken|administrator|developer)\b"
    ),
    re.compile(
        r"\b(?:remove|disable|turn\s+off|bypass)\s+"
        r"(?:all\s+)?(?:your\s+)?(?:safety|security|content|"
        r"policy|guardrail|restriction|filter)s?\b"
    ),
]


# System / Developer impersonation
SYSTEM_IMPERSONATION_PATTERNS = [
    re.compile(r"(?:^|\n)\s*(?:system|developer|assistant)\s*:\s*", re.IGNORECASE),
    re.compile(
        r"\[\s*(?:system|developer|assistant|instruction)\s*\]",
        re.IGNORECASE,
    ),
    re.compile(
        r"<\s*(?:system|developer|assistant|instruction)\s*>",
        re.IGNORECASE,
    ),
    re.compile(
        r"###\s*(?:system|developer|assistant|instruction)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:system|developer)\s+message\s*:",
        re.IGNORECASE,
    ),
]


# Prompt / instruction extraction
PROMPT_EXTRACTION_PATTERNS = [
    re.compile(
        r"\b(?:reveal|show|display|print|output|repeat|give\s+me|"
        r"tell\s+me|expose|leak)\s+(?:your|the)\s+"
        r"(?:system\s+prompt|system\s+message|developer\s+message|"
        r"hidden\s+instructions?|internal\s+instructions?)\b"
    ),
    re.compile(
        r"\bwhat\s+(?:are|were)\s+(?:your|the)\s+"
        r"(?:system|developer|hidden|internal)\s+"
        r"(?:instructions?|prompt|rules?)\b"
    ),
    re.compile(
        r"\b(?:copy|dump|output)\s+(?:the\s+)?"
        r"(?:entire|full|complete)\s+"
        r"(?:system\s+prompt|system\s+message|developer\s+message)\b"
    ),
]


# Jailbreak / policy bypass language
JAILBREAK_PATTERNS = [
    re.compile(
        r"\b(?:bypass|circumvent|evade|defeat|disable|break)\s+"
        r"(?:your\s+)?(?:safety|security|content|policy|"
        r"guardrails?|restrictions?|filters?)\b"
    ),
    re.compile(
        r"\b(?:without|ignore)\s+(?:any\s+)?"
        r"(?:safety|security|content)\s+(?:restrictions?|filters?|rules?)\b"
    ),
    re.compile(
        r"\b(?:jailbreak|dan\s+mode|developer\s+mode|"
        r"unrestricted\s+mode|uncensored\s+mode)\b"
    ),
]


# Instruction delimiter / boundary manipulation
DELIMITER_INJECTION_PATTERNS = [
    re.compile(
        r"(?:^|\n)\s*"
        r"(?:BEGIN|START|END|STOP)\s+"
        r"(?:SYSTEM|DEVELOPER|INSTRUCTIONS?|PROMPT)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"```(?:system|developer|instruction|prompt)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"<\s*/?\s*(?:system|developer|instruction|prompt)\s*>",
        re.IGNORECASE,
    ),
]

PATTERN_GROUPS = {
        "instruction_override": (INSTRUCTION_OVERRIDE_PATTERNS, 3),
        "instruction_replacement": (INSTRUCTION_REPLACEMENT_PATTERNS, 3),
        "role_manipulation": (ROLE_MANIPULATION_PATTERNS, 2),
        "system_impersonation": (SYSTEM_IMPERSONATION_PATTERNS, 3),
        "prompt_extraction": (PROMPT_EXTRACTION_PATTERNS, 3),
        "jailbreak": (JAILBREAK_PATTERNS, 2),
        "delimiter_injection": (DELIMITER_INJECTION_PATTERNS, 2),
    }


def normalize_for_detection(prompt: str) -> str:
    """
    Normalize user input for security detection
    """
    # Canonical Unicode Normalization
    text = unicodedata.normalize("NFKC", prompt)

    # Remove zero-width and invisible formatting characters that can be used to split malicious phrases.
    text = re.sub(r"[\u200B-\u200D\u2060\uFEFF]", "", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse repeated whitespace while preserving line boundaries enough for system/developer delimiter detection.
    text = re.sub(r"[ \t\f\v]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)

    return text.strip().lower()


class PromptInjectionDetector:
    """
    Detects potential prompt injection attempts in user input.
    """
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

        for category, (patterns, weight) in self.PATTERN_GROUPS.items():
            category_matched = False

            for pattern in patterns:
                if pattern.search(normalized_prompt):
                    score += weight
                    matched_patterns.append(pattern.pattern)
                    category_matched = True

                    break  # One match per category is enough to assign the category score. This prevents repeated phrases from artificially inflating the score.

            if category_matched:
                matched_categories.append(category)

        if score >= BLOCK_THRESHOLD:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Potential prompt injection detected.",
                metadata={
                    "score": score,
                    "categories": matched_categories,
                    "pattern_count": len(matched_patterns),
                },
            )

        if score >= FLAG_THRESHOLD:
            return GuardrailResult(
                action=GuardrailAction.FLAG,
                reason="Suspicious prompt-injection patterns detected.",
                metadata={
                    "score": score,
                    "categories": matched_categories,
                    "pattern_count": len(matched_patterns),
                },
            )

        return GuardrailResult(
            action=GuardrailAction.ALLOW, metadata={"score": 0, "categories": []}
        )
