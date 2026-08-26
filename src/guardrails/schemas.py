from dataclasses import dataclass, field
from enum import Enum


class GuardrailAction(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    SANITIZE = "sanitize"
    FLAG = "flag"


@dataclass
class GuardrailResult:
    action: GuardrailAction
    reason: str | None = None
    sanitized: str | None = None
    metadata: dict = field(default_factory=dict)


class GuardrailException(Exception):
    def __init__(self, stage: str, reason: str):
        self.stage = stage
        self.reason = reason
        super().__init__(f"[{stage}] {reason}")
