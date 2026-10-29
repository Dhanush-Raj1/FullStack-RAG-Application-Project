import re
import unicodedata
from collections.abc import Mapping, Sequence

from src.guardrails.schemas import GuardrailAction, GuardrailResult

DEFAULT_SCOPE_KNOWLEDGE = (
    # NemoClaw documentation
    "NemoClaw architecture, system components, and technical design",
    "NemoClaw ecosystem, integrations, and supported technologies",
    "NemoClaw inference options, inference configuration, and deployment",
    "NemoClaw overview, core concepts, and functionality",
    "NemoClaw release notes, updates, and version changes",

    # Apple product specifications
    "Apple Watch Ultra 3 technical specifications and features",
    "iPhone 16 Pro technical specifications, hardware, and features",
    "iPhone 17 Pro technical specifications, hardware, and features",
    "MacBook Air 13-inch M5 specifications, hardware, and features",
    "MacBook Air 15-inch M5 specifications, hardware, and features",
    "Comparisons between the indexed Apple devices and their specifications",

    # NASA and space exploration
    "Apollo 11 mission objectives, history, and achievements",
    "NASA Artemis Program objectives, missions, and lunar exploration",
    "NASA Curiosity Rover, its instruments, discoveries, and Mars exploration",
    "James Webb Space Telescope, its instruments, observations, and discoveries",
    "Voyager 1 spacecraft, mission history, scientific discoveries, and interstellar exploration",

    # Cross-document questions
    "Summaries, explanations, and comparisons based on the indexed documents",
    "Questions that combine information from multiple documents in the knowledge base",
)


DEFAULT_OFF_TOPIC_PATTERNS: Mapping[str, str] = {
    "cooking_and_recipes": (
        r"\b(?:"
        r"recipe\s+for|"
        r"how\s+to\s+cook|"
        r"cooking\s+instructions\s+for|"
        r"ingredients\s+for\s+(?:making|cooking)"
        r")\b"
    ),
    "sports_results": (
        r"\b(?:"
        r"live\s+(?:cricket|football|soccer|tennis)\s+scores?|"
        r"(?:cricket|football|soccer|tennis)\s+match\s+results?"
        r")\b"
    ),
    "entertainment_recommendations": (
        r"\b(?:"
        r"recommend\s+(?:a\s+)?(?:movie|film|tv\s+series)|"
        r"best\s+(?:movies|films|tv\s+series)\s+to\s+watch"
        r")\b"
    ),
    "personal_finance_calculations": (
        r"\b(?:"
        r"calculate\s+my\s+(?:income\s+tax|home\s+loan\s+emi)|"
        r"best\s+(?:stocks|mutual\s+funds)\s+to\s+buy"
        r")\b"
    ),
}


def normalize_for_detection(query: str) -> str:
    """
    Normalize text for consistent matching without changing user input.
    """

    text = unicodedata.normalize("NFKC", query)

    # Remove common zero-width characters.
    text = re.sub(r"[\u200B-\u200D\u2060\uFEFF]", "", text)

    # Normalize line endings and repeated whitespace.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\s+", " ", text)

    return text.strip().casefold()


class OffTopicDetector:
    """
    Detects queries that may fall outside the configurated RAG Scope.
    """

    def __init__(
        self,
        scope_keywords: Sequence[str] = DEFAULT_SCOPE_KNOWLEDGE,
        off_topic_patterns: Mapping[str, str] = DEFAULT_OFF_TOPIC_PATTERNS,
    ) -> None:
        self.scope_patterns = [
            (
                keyword,
                re.compile(r"(?<!\w)" + re.escape(keyword.casefold()) + r"(?!\w)"),
            )
            for keyword in scope_keywords
            if keyword and keyword.strip()
        ]

        self.off_topic_patterns = {
            category: re.compile(pattern, re.IGNORECASE)
            for category, pattern in off_topic_patterns.items()
        }

    def scan(self, prompt: str) -> GuardrailResult:
        if prompt is None:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Input cannot be null.",
            )

        if not isinstance(prompt, str):
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Input must be a string",
            )

        if not prompt.strip():
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Input cannot be empty.",
            )

        normalized_prompt = normalize_for_detection(prompt)

        # explicitly configured out-of-scope categories
        matched_categories = [
            category
            for category, pattern in self.off_topic_patterns.items()
            if pattern.search(normalized_prompt)
        ]

        if matched_categories:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Query matches the configured out-of-scope category.",
                metadata={
                    "matched_categories": matched_categories,
                    "detector": "off_topic",
                },
            )

        # Indicators of the configured application scope
        matched_keywords = [
            keyword
            for keyword, pattern in self.scope_patterns
            if pattern.search(normalized_prompt)
        ]

        if matched_keywords:
            return GuardrailResult(
                action=GuardrailAction.ALLOW,
                reason="Query matches configured in-scope indicators",
                metadata={
                    "matched_scope_indicators": matched_keywords,
                    "detector": "off_topic",
                },
            )

        # not match does not prove a query is off-topic
        return GuardrailResult(
            action=GuardrailAction.FLAG,
            reason="Unable to determine whether the query is out-of-scope",
            metadata={
                "detector": "off_topic",
                "scope_match": False,
            },
        )
