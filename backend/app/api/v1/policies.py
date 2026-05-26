from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.engines.firewall import firewall
from app.engines.policy import PolicyDecision
from app.models.policy import Policy
from app.models.user import User

router = APIRouter(prefix="/policies", tags=["policies"])


class PolicyCreate(BaseModel):
    name: str
    llm_connection_id: UUID | None = None
    allowed_tools: list[str] = []
    forbidden_phrases: list[str] = []
    allowed_domains: list[str] = []
    max_token_budget: int = 100000
    allowed_providers: list[str] = []
    pii_policy: str = "redact"
    prompt_length_limit: int = 32000
    compliance_mode: str = "standard"
    custom_regex_patterns: list[dict] = []
    default_action: str = "warn"
    rules: dict = {}
    priority: int = 100


class PolicyResponse(BaseModel):
    id: UUID
    name: str
    pii_policy: str
    default_action: str
    compliance_mode: str
    is_active: bool

    class Config:
        from_attributes = True


class FirewallRequest(BaseModel):
    prompt: str
    policy_id: UUID | None = None


@router.get("", response_model=list[PolicyResponse])
async def list_policies(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    q = select(Policy).where(Policy.is_active == True)
    if user.organization_id:
        q = q.where(Policy.organization_id == user.organization_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=PolicyResponse)
async def create_policy(data: PolicyCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    policy = Policy(
        organization_id=user.organization_id or UUID("00000000-0000-0000-0000-000000000001"),
        **data.model_dump(),
    )
    db.add(policy)
    await db.flush()
    return policy


@router.post("/firewall/intercept")
async def intercept_prompt(data: FirewallRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    policy_dict = {
        "pii_policy": "redact",
        "forbidden_phrases": ["ignore all rules"],
        "prompt_length_limit": 32000,
        "default_action": "warn",
        "custom_regex_patterns": [],
        "allowed_domains": [],
    }
    if data.policy_id:
        p = await db.get(Policy, data.policy_id)
        if p:
            policy_dict = {
                "pii_policy": p.pii_policy,
                "forbidden_phrases": p.forbidden_phrases,
                "allowed_domains": p.allowed_domains,
                "prompt_length_limit": p.prompt_length_limit,
                "default_action": p.default_action,
                "custom_regex_patterns": p.custom_regex_patterns,
            }
    result = await firewall.intercept(data.prompt, policy_dict, str(user.organization_id or ""))
    return {
        "allowed": result.allowed,
        "decision": result.decision,
        "redacted_prompt": result.redacted_prompt,
        "detections": result.detections,
        "pii_matches": result.pii_matches,
        "latency_ms": result.latency_ms,
        "request_id": result.request_id,
    }
