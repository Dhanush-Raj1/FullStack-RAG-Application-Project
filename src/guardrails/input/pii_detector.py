import re
import unicodedata

from src.guardrails.schemas import GuardrailAction, GuardrailResult

PII_PATTERNS = {
    "email": re.compile(
        r"\b[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@[a-zA-Z0-9-]+"
        r"(?:\.[a-zA-Z0-9-]+)+\b"
    ),
    "phone": re.compile(
        r"(?<!\d)"
        r"(?:\+\d{1,3}[\s.-]?)?"
        r"(?:\(?\d{2,4}\)?[\s.-]?)?"
        r"\d{3,4}[\s.-]?\d{3,4}"
        r"(?!\d)"
    ),
    "ssn": re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
    "aadhaar": re.compile(
        r"(?<!\d)"
        r"(?:\d{4}[\s-]?){2}\d{4}"
        r"(?!\d)"
    ),
    "pan": re.compile(
        r"(?<![A-Za-z0-9])"
        r"[A-Z]{5}[0-9]{4}[A-Z]"
        r"(?![A-Za-z0-9])",
        re.IGNORECASE,
    ),
    "passport": re.compile(
        r"(?<![A-Za-z0-9])"
        r"[A-Z]{1,2}[0-9]{6,8}"
        r"(?![A-Za-z0-9])",
        re.IGNORECASE,
    ),
    "ipv4": re.compile(
        r"(?<![\d.])"
        r"(?:"
        r"(?:25[0-5]|2[0-4]\d|1?\d?\d)\."
        r"){3}"
        r"(?:25[0-5]|2[0-4]\d|1?\d?\d)"
        r"(?![\d.])"
    ),
    "date_of_birth": re.compile(
        r"\b(?:"
        r"date\s+of\s+birth|"
        r"dob|"
        r"birth\s+date"
        r")\s*[:=-]?\s*"
        r"\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}"
        r"\b",
        re.IGNORECASE,
    ),
    "ifsc": re.compile(
        r"(?<![A-Za-z0-9])"
        r"[A-Z]{4}0[A-Z0-9]{6}"
        r"(?![A-Za-z0-9])",
        re.IGNORECASE,
    ),
    "upi_id": re.compile(
        r"(?<![\w.+-])"
        r"[A-Za-z0-9][A-Za-z0-9._-]{1,255}"
        r"@(?:okhdfcbank|okicici|oksbi|okaxis|ybl|paytm|upi|apl|ibl|axl)"
        r"(?![\w.-])",
        re.IGNORECASE,
    ),
    "bank_account": re.compile(
        r"\b(?:"
        r"account\s*(?:number|no|#)|"
        r"bank\s+account"
        r")\s*[:=-]?\s*"
        r"\d{9,18}\b",
        re.IGNORECASE,
    ),
}

# credit card detection (kept separate due to Luhn validation)
CREDIT_CARD_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\d[ -]?){13,19}"
    r"(?!\d)"
)


# credit card validation
def passes_luhn(card_number: str) -> bool:
    """
    Validate a credit card number using the Luhn algorithm.
    """

    digits = re.sub(r"\D", "", card_number)

    if not 13 <= len(digits) <= 19:
        return False

    total = 0
    parity = len(digits) % 2

    for index, digit in enumerate(digits):
        value = int(digit)

        if index % 2 == parity:
            value *= 2

            if value > 9:
                value -= 9

        total += value

    return total % 10 == 0


def normalize_for_detection(query: str) -> str:
    """
    Normalize user's query for PII detection
    """

    text = unicodedata.normalize("NFKC", query)
    text = re.sub(
        r"[\u200B-\u200D\u2060\uFEFF]",
        "",
        text,
    )
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\f\v]+", " ", text)

    return text.strip()


class PIIDetector:
    """
    Detects Personally Identifiable Information (PII) in the user's input.
    """

    def scan(self, prompt: str) -> GuardrailResult:
        if prompt is None:
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Input cannot be null."
            )

        if not isinstance(prompt, str):
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Input must be a string."
            )

        if not prompt.strip():
            return GuardrailResult(
                action=GuardrailAction.BLOCK, reason="Input cannot be empty."
            )

        normalized_prompt = normalize_for_detection(prompt)

        found = {}

        for pii_type, pattern in PII_PATTERNS.items():
            matches = pattern.findall(normalized_prompt)

            if matches:
                found[pii_type] = len(matches)

        credit_card_matches = CREDIT_CARD_PATTERN.finditer(normalized_prompt)

        valid_cards = [
            match.group() for match in credit_card_matches if passes_luhn(match.group())
        ]

        if valid_cards:
            found["credit_card"] = len(valid_cards)

        if found:
            return GuardrailResult(
                action=GuardrailAction.FLAG,
                reason=(
                    "Query contains potentially sensitive "
                    "personally identifiable information."
                ),
                metadata={"pii_found": found},
            )

        return GuardrailResult(
            action=GuardrailAction.ALLOW,
            metadata={"pii_found": {}},
        )
