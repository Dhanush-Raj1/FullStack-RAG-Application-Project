import math
import re
import unicodedata
from collections.abc import Mapping, Sequence

from src.core.embedding import GeminiEmbeddingGenerator
from src.guardrails.schemas import GuardrailAction, GuardrailResult

SCOPE_KNOWLEDGE = (
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

OFF_TOPIC_KNOWLEDGE = (
    "Cooking, recipes, food preparation, and meal planning",
    "Sports matches, sports scores, teams, tournaments, and sports news",
    "Movies, television series, music, entertainment, and celebrity recommendations",
    "Personal finance, stock investing, mutual funds, loans, taxes, and financial advice",
)

OFF_TOPIC_PATTERNS: Mapping[str, str] = {
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


def cosine_similarity(
    vector_a: Sequence[float],
    vector_b: Sequence[float],
) -> float:
    """
    Computes the cosine similarity between two vectors.
    Returns a value between -1 and 1.
    """

    if not vector_a and vector_b:
        raise ValueError("Vectors cannot be empty.")

    if len(vector_a) != len(vector_b):
        raise ValueError("Vectors must be of the same dimensionality.")

    dot_product = sum(a * b for a, b in zip(vector_a, vector_b))

    magnitude_a = math.sqrt(sum(a * a for a in vector_a))

    magnitude_b = math.sqrt(sum(b * b for b in vector_b))

    if magnitude_a == 0 or magnitude_b == 0:
        raise ValueError("Cannot calculate similarity for zero vector.")

    return dot_product / (magnitude_a * magnitude_b)


class OffTopicDetector:
    """
    Detects queries that may fall outside the configurated RAG Scope.
    """

    def __init__(
        self,
        embedder: GeminiEmbeddingGenerator,
        scope_knowledge: Sequence[str] = SCOPE_KNOWLEDGE,
        off_topic_knowledge: Sequence[str] = OFF_TOPIC_KNOWLEDGE,
        off_topic_patterns: Mapping[str, str] = OFF_TOPIC_PATTERNS,
    ) -> None:

        self.embedder = embedder

        self.scope_knowledge = tuple(
            item.strip() for item in scope_knowledge if item and item.strip()
        )

        self.off_topic_knowledge = tuple(
            item.strip() for item in off_topic_knowledge if item and item.strip()
        )

        self.scope_embeddings: list[list[float]] = []
        self.off_topic_embeddings: list[list[float]] = []

        self.scope_patterns = [
            (
                keyword,
                re.compile(r"(?<!\w)" + re.escape(keyword.casefold()) + r"(?!\w)"),
            )
            for keyword in self.scope_knowledge
        ]

        self.off_topic_patterns = {
            category: re.compile(pattern, re.IGNORECASE)
            for category, pattern in off_topic_patterns.items()
        }

        self._initialize_reference_embeddings()

    def _initialize_reference_embeddings(self) -> None:
        """
        Generate embeddings once when the detector is initialized
        """

        if self.scope_knowledge:
            self.scope_embeddings = self.embedder.embed_texts(
                list(self.scope_knowledge),
                task_type="RETRIEVAL_DOCUMENT",
            )

        if self.off_topic_knowledge:
            self.off_topic_embeddings = self.embedder.embed_texts(
                list(self.off_topic_knowledge),
                task_type="RETRIEVAL_DOCUMENT",
            )

        if len(self.scope_embeddings) != len(self.scope_knowledge):
            raise RuntimeError(
                "Scope Embeddings count does not match scope knowledge count."
            )

        if len(self.off_topic_embeddings) != len(self.off_topic_knowledge):
            raise RuntimeError(
                "Off-topic Embeddings count does not match off-topic knowledge count."
            )

    def _max_similarity(
        self,
        query_embedding: Sequence[float],
        reference_embeddings: Sequence[Sequence[float]],
        reference_texts: Sequence[str],
    ) -> tuple[float, str | None]:
        """
        Returns the highest cosine similarity and its
        corresponding reference text.
        """

        if not reference_embeddings:
            return 0.0, None

        best_score = -1.0
        best_match = None

        for reference_text, reference_embedding in zip(
            reference_texts,
            reference_embeddings,
        ):
            score = cosine_similarity(
                query_embedding,
                reference_embedding,
            )

            if score > best_score:
                best_score = score
                best_match = reference_text

        return best_score, best_match

    def scan(
        self,
        prompt: str,
        query_embedding: Sequence[float] | None = None,
    ) -> GuardrailResult:

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

        # Layer 1: Explicit off-topic detection
        matched_categories = [
            category
            for category, pattern in self.off_topic_patterns.items()
            if pattern.search(normalized_prompt)
        ]

        if matched_categories:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Query matches a configured out-of-scope category.",
                metadata={
                    "detector": "off_topic",
                    "detection_method": "explicit_pattern",
                    "matched_categories": matched_categories,
                },
            )

        # Layer 2: Semantic Detection
        if query_embedding is None:
            return GuardrailResult(
                action=GuardrailAction.FLAG,
                reason=(
                    "Query embedding was not provided; "
                    "semantic scope detection could not be performed."
                ),
                metadata={
                    "detector": "off_topic",
                    "detection_method": "semantic",
                    "semantic_check": False,
                },
            )

        scope_score, scope_match = self._max_similarity(
            query_embedding,
            self.scope_embeddings,
            self.scope_knowledge,
        )

        off_topic_score, off_topic_match = self._max_similarity(
            query_embedding,
            self.off_topic_embeddings,
            self.off_topic_knowledge,
        )

        # Layer 3: Decision framework
        SCOPE_ALLOW_THRESHOLD = 0.75
        OFF_TOPIC_BLOCK_THRESHOLD = 0.75

        if (
            off_topic_score >= OFF_TOPIC_BLOCK_THRESHOLD
            and off_topic_score > scope_score
        ):
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Query is semantically classified as out-of-scope.",
                metadata={
                    "detector": "off_topic",
                    "detection_method": "semantic",
                    "scope_score": round(scope_score, 4),
                    "scope_match": scope_match,
                    "off_topic_score": round(off_topic_score, 4),
                    "off_topic_match": off_topic_match,
                },
            )

        if scope_score >= SCOPE_ALLOW_THRESHOLD and scope_score > off_topic_score:
            return GuardrailResult(
                action=GuardrailAction.ALLOW,
                reason="Query is semantically classified as in-scope.",
                metadata={
                    "detector": "off_topic",
                    "detection_method": "semantic",
                    "scope_score": round(scope_score, 4),
                    "scope_match": scope_match,
                    "off_topic_score": round(off_topic_score, 4),
                    "off_topic_match": off_topic_match,
                },
            )

        return GuardrailResult(
            action=GuardrailAction.FLAG,
            reason="Unable to confidently determine whether the query is in-scope.",
            metadata={
                "detector": "off_topic",
                "detection_method": "semantic",
                "scope_score": round(scope_score, 4),
                "scope_match": scope_match,
                "off_topic_score": round(off_topic_score, 4),
                "off_topic_match": off_topic_match,
            },
        )
