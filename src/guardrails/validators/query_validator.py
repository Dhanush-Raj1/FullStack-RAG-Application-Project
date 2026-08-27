from src.guardrails.schemas import GuardrailAction, GuardrailResult

MAX_QUERY_LEN = 2000


class QueryValidator:
    def validate(self, question: str) -> GuardrailResult:
        if question is None or not question.strip():
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Question cannot be empty."
            )

        q = question.strip()
        if len(q) > MAX_QUERY_LEN:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason=f"Question exceeds maximum length of {MAX_QUERY_LEN} characters.",
            )

        alnum_ratio = sum(c.isalnum() for c in q) / max(len(q), 1)
        if alnum_ratio < 0.2:
            return GuardrailResult(
                action=GuardrailAction.BLOCK,
                reason="Question does not contain enough readable content.",
            )

        return GuardrailResult(action=GuardrailAction.ALLOW, sanitized=q)
