from src.guardrails.schemas import GuardrailAction, GuardrailResult

MAX_QUERY_LEN = 2000


class QueryValidator:
    """
    Validates the user's query input.
    """

    def validate(self, query: str) -> GuardrailResult:
        if query is None:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Query cannot be null."
            )

        if not isinstance(query, str):
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Query must be a string."
            )

        sanitized_query = query.strip()

        if not sanitized_query:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Query cannot be empty."
            )

        if len(sanitized_query) > MAX_QUERY_LEN:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason=f"Query exceeds maximum length of {MAX_QUERY_LEN} characters.",
            )

        alnum_ratio = sum(c.isalnum() for c in sanitized_query) / len(sanitized_query)  # alphanumeric character ratio

        if alnum_ratio < 0.2:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Query does not contain enough readable content.",
            )

        return GuardrailResult(action=GuardrailAction.ALLOW, sanitized=sanitized_query)
