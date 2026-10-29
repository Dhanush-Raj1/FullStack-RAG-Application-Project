# import re

# from src.guardrails.schemas import GuardrailAction, GuardrailResult

# DISALLOWED_PATTERNS = [
#     re.compile(r"(?i)\b(bomb|explosive)\s+(making|recipe|instructions)\b"),
#     re.complie(r"(?i)how to (hack|breach)\b.*\b(bank|server|account)\b"),
# ]


# class OffTopicDetector:
#     def scan(self, prompt: str) -> GuardrailResult:
#         for pattern in DISALLOWED_PATTERNS:
#             if pattern.search(prompt):
#                 return GuardrailResult(
#                     action=GuardrailAction.BLOCK,
#                     reason="Query is off-topic and irrelevant.",
#                 )

#         return GuardrailResult(action=GuardrailAction.ALLOW)


import re
import unicodedata
from typing import Mapping, Sequence

from src.guardrails.schemas import GuardrailAction, GuardrailResult

# Scope of the RAG Chatbot
DEFAULT_SCOPE_KNOWLEDGE = ()


DEFAULT_OFF_TOPIC_PATTERNS: Mapping[str, str] = {}


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
            off_topic_patterns: Mapping[str, str] = DEFAULT_OFF_TOPIC_PATTERNS
    ) -> None:
        self.scope_patterns = [
            (
                keyword,
                re.compile(
                    r"(?<!\w)"
                    + re.escape(keyword.casefold())
                    + r"(?!\w)"
                ),
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
            return GuardrailResult(action=GuardrailAction.BLOCK,
                                   reason="Input cannot be null.",)

        if not isinstance(prompt, str):
            return GuardrailResult(action=GuardrailAction.BLOCK,
                                   reason="Input must be a string",)
            
        if not prompt.strip():
            return GuardrailResult(action=GuardrailAction.BLOCK, 
                                   reason="Input cannot be empty.",)

        normalized_prompt = normalize_for_detection(prompt)

        # explicitly configured out-of-scope categories
        matched_categories = [
            category
            for category, pattern in self.off_topic_patterns.items()
            if pattern.search(normalized_prompt)
        ]

        if matched_categories:
            return GuardrailResult(action=GuardrailAction.BLOCK,
                                   reason="Query matches the configured out-of-scope category.",
                                   metadata={
                                       "matched_categories": matched_categories,
                                       "detector": "off_topic",
                                   },)

        # Indicators of the configured application scope
        matched_keywords = [
            keyword
            for keyword, pattern in self.scope_patterns
            if pattern.search(normalized_prompt)
        ]

        if matched_keywords: 
            return GuardrailResult(action=GuardrailAction.ALLOW,
                                   reason="Query matches configured in-scope indicators",
                                   metadata={
                                       "matched_scope_indicators": matched_keywords,
                                       "detector": "off_topic",
                                   },)

        # not match does not prove a query is off-topic
        return GuardrailResult(action=GuardrailAction.FLAG,
                               reason="Unable to determine whether the query is out-of-scope",
                               metadata={
                                   "detector": "off_topic",
                                   "scope_match": False,
                               },)

        
        



