"""Policy decision engine — Allow, Warn, Quarantine, Redact, Block."""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.engines.pii import PIIRedactionEngine, PIIAction


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    QUARANTINE = "quarantine"
    REDACT = "redact"
    BLOCK = "block"


@dataclass
class PolicyEvaluation:
    decision: PolicyDecision
    reasons: list[str]
    redacted_prompt: Optional[str] = None
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PolicyEngine:
    def evaluate(
        self,
        prompt: str,
        policy: dict,
        pii_engine_instance: Optional[PIIRedactionEngine] = None,
    ) -> PolicyEvaluation:
        reasons: list[str] = []
        decision = PolicyDecision.ALLOW
        redacted = prompt

        pii_action_map = {
            "allow": PIIAction.ALLOW,
            "warn": PIIAction.WARN,
            "redact": PIIAction.REDACT,
            "block": PIIAction.BLOCK,
        }
        pii_policy = policy.get("pii_policy", "redact")
        engine = pii_engine_instance or PIIRedactionEngine(
            custom_patterns=policy.get("custom_regex_patterns", []),
            default_action=pii_action_map.get(pii_policy, PIIAction.REDACT),
        )
        pii_result = engine.scan(prompt, pii_action_map.get(pii_policy))
        if pii_result.matches:
            reasons.append(f"PII detected: {len(pii_result.matches)} entities")
            if pii_result.action == PIIAction.BLOCK:
                return PolicyEvaluation(decision=PolicyDecision.BLOCK, reasons=reasons + ["PII policy: block"])
            if pii_result.action == PIIAction.REDACT:
                decision = PolicyDecision.REDACT
                redacted = pii_result.redacted_text
            elif pii_result.action == PIIAction.WARN:
                decision = PolicyDecision.WARN

        max_len = policy.get("prompt_length_limit", 32000)
        if len(prompt) > max_len:
            reasons.append(f"Prompt exceeds length limit ({max_len})")
            decision = PolicyDecision.BLOCK

        forbidden = policy.get("forbidden_phrases", [])
        prompt_lower = prompt.lower()
        for phrase in forbidden:
            if phrase.lower() in prompt_lower:
                reasons.append(f"Forbidden phrase: {phrase}")
                decision = PolicyDecision.BLOCK

        allowed_domains = policy.get("allowed_domains", [])
        if allowed_domains:
            import re
            urls = re.findall(r"https?://([^\s/]+)", prompt)
            for domain in urls:
                if not any(domain.endswith(d) or domain == d for d in allowed_domains):
                    reasons.append(f"Domain not allowed: {domain}")
                    decision = PolicyDecision.QUARANTINE

        default_action = policy.get("default_action", "warn")
        if decision == PolicyDecision.ALLOW and default_action != "allow":
            action_map = {
                "warn": PolicyDecision.WARN,
                "quarantine": PolicyDecision.QUARANTINE,
                "redact": PolicyDecision.REDACT,
                "block": PolicyDecision.BLOCK,
            }
            if not reasons:
                decision = action_map.get(default_action, PolicyDecision.ALLOW)

        return PolicyEvaluation(decision=decision, reasons=reasons, redacted_prompt=redacted, metadata={"pii_count": len(pii_result.matches)})


policy_engine = PolicyEngine()
