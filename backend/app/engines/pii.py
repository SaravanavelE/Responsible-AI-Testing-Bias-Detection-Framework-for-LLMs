"""PII redaction engine — regex, checksum, entropy detection."""
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class PIIAction(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    REDACT = "redact"
    BLOCK = "block"


@dataclass
class PIIMatch:
    type: str
    value: str
    start: int
    end: int
    confidence: float
    action: PIIAction = PIIAction.REDACT


@dataclass
class PIIScanResult:
    matches: List[PIIMatch] = field(default_factory=list)
    action: PIIAction = PIIAction.ALLOW
    redacted_text: str = ""


def _luhn_check(number: str) -> bool:
    digits = [int(d) for d in number if d.isdigit()]
    if len(digits) < 13:
        return False
    checksum = 0
    reverse = digits[::-1]
    for i, d in enumerate(reverse):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def _entropy(s: str) -> float:
    if not s:
        return 0.0
    import math
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    length = len(s)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


PII_PATTERNS = {
    "email": (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", 0.95),
    "phone": (r"\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", 0.85),
    "ssn": (r"\b\d{3}-\d{2}-\d{4}\b", 0.9),
    "credit_card": (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", 0.8),
    "aadhaar": (r"\b\d{4}\s?\d{4}\s?\d{4}\b", 0.75),
    "pan": (r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", 0.9),
    "api_key": (r"\b(?:sk|pk|api)[-_]?[a-zA-Z0-9]{16,}\b", 0.92),
    "jwt": (r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b", 0.95),
    "ip_address": (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", 0.7),
    "bank_account": (r"\b\d{9,18}\b", 0.5),
    "secret": (r"(?:password|secret|token)\s*[:=]\s*['\"]?[^\s'\"]{8,}", 0.88),
}


class PIIRedactionEngine:
    def __init__(self, custom_patterns: Optional[List[dict]] = None, default_action: PIIAction = PIIAction.REDACT):
        self.custom_patterns = custom_patterns or []
        self.default_action = default_action

    def scan(self, text: str, policy_action: Optional[PIIAction] = None) -> PIIScanResult:
        matches: List[PIIMatch] = []
        action = policy_action or self.default_action

        for pii_type, (pattern, confidence) in PII_PATTERNS.items():
            for m in re.finditer(pattern, text, re.I):
                value = m.group()
                if pii_type == "credit_card" and not _luhn_check(re.sub(r"\D", "", value)):
                    continue
                if pii_type == "bank_account" and _entropy(value) < 2.5:
                    continue
                matches.append(
                    PIIMatch(
                        type=pii_type,
                        value=value,
                        start=m.start(),
                        end=m.end(),
                        confidence=confidence,
                        action=action,
                    )
                )

        for custom in self.custom_patterns:
            pattern = custom.get("pattern", "")
            if pattern:
                for m in re.finditer(pattern, text):
                    matches.append(
                        PIIMatch(
                            type=custom.get("name", "custom"),
                            value=m.group(),
                            start=m.start(),
                            end=m.end(),
                            confidence=0.8,
                            action=action,
                        )
                    )

        redacted = text
        for match in sorted(matches, key=lambda x: x.start, reverse=True):
            if match.action in (PIIAction.REDACT, PIIAction.BLOCK):
                mask = f"[REDACTED:{match.type.upper()}]"
                redacted = redacted[: match.start] + mask + redacted[match.end :]

        final_action = PIIAction.ALLOW
        if any(m.action == PIIAction.BLOCK for m in matches):
            final_action = PIIAction.BLOCK
        elif any(m.action == PIIAction.REDACT for m in matches):
            final_action = PIIAction.REDACT
        elif any(m.action == PIIAction.WARN for m in matches):
            final_action = PIIAction.WARN

        return PIIScanResult(matches=matches, action=final_action, redacted_text=redacted)


pii_engine = PIIRedactionEngine()
