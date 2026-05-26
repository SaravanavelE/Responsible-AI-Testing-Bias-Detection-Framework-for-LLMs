"""Live prompt firewall — real-time interception middleware."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid

from app.engines.detection import detection_engine
from app.engines.policy import PolicyEngine, PolicyDecision
from app.engines.pii import PIIRedactionEngine, PIIAction


@dataclass
class FirewallResult:
    allowed: bool
    decision: str
    prompt: str
    redacted_prompt: Optional[str]
    detections: list
    pii_matches: int
    latency_ms: float
    request_id: str
    timestamp: str


class LivePromptFirewall:
    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.blocked_injection_count = 0
        self.blocked_dlp_count = 0

    async def intercept(self, prompt: str, policy: dict, tenant_id: str) -> FirewallResult:
        import time
        start = time.perf_counter()
        request_id = str(uuid.uuid4())

        pii_engine = PIIRedactionEngine(
            custom_patterns=policy.get("custom_regex_patterns", []),
            default_action=PIIAction(policy.get("pii_policy", "redact")),
        )
        policy_eval = self.policy_engine.evaluate(prompt, policy, pii_engine)
        detections = []
        pre_detection = detection_engine.analyze(prompt, "")
        if pre_detection.detected:
            detections.append(pre_detection.detection_type.value if pre_detection.detection_type else "unknown")

        allowed = policy_eval.decision not in (PolicyDecision.BLOCK, PolicyDecision.QUARANTINE)
        if pre_detection.detected and pre_detection.severity in ("critical", "high"):
            allowed = False
            if "injection" in str(pre_detection.detection_type):
                self.blocked_injection_count += 1
            if "leakage" in str(pre_detection.detection_type):
                self.blocked_dlp_count += 1

        latency = (time.perf_counter() - start) * 1000
        return FirewallResult(
            allowed=allowed,
            decision=policy_eval.decision.value,
            prompt=prompt,
            redacted_prompt=policy_eval.redacted_prompt,
            detections=detections,
            pii_matches=policy_eval.metadata.get("pii_count", 0),
            latency_ms=latency,
            request_id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


firewall = LivePromptFirewall()
