from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.encryption import vault
from app.engines.llm_client import LLMClient, PROVIDER_PRESETS
from app.models.llm_connection import LLMConnection
from app.models.user import User
from app.schemas.llm import LLMConnectionCreate, LLMConnectionResponse, LLMConnectionUpdate, ProviderPreset
from app.services.audit import log_audit

router = APIRouter(prefix="/llm-connections", tags=["llm-connections"])


@router.get("/presets", response_model=list[ProviderPreset])
async def get_provider_presets():
    return [
        ProviderPreset(provider=k, **{kk: vv for kk, vv in v.items() if kk != "models"}, models=v.get("models", []))
        for k, v in PROVIDER_PRESETS.items()
    ]


@router.get("", response_model=list[LLMConnectionResponse])
async def list_connections(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    q = select(LLMConnection).where(LLMConnection.is_active == True)
    if user.organization_id:
        q = q.where(LLMConnection.organization_id == user.organization_id)
    result = await db.execute(q.order_by(LLMConnection.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=LLMConnectionResponse)
async def create_connection(data: LLMConnectionCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    preset = PROVIDER_PRESETS.get(data.provider.lower(), {})
    conn = LLMConnection(
        organization_id=user.organization_id or UUID("00000000-0000-0000-0000-000000000001"),
        name=data.name,
        provider=data.provider,
        api_key_encrypted=vault.encrypt(data.api_key),
        api_base_url=data.api_base_url or preset.get("api_base_url", ""),
        model_name=data.model_name,
        custom_headers=data.custom_headers,
        response_json_path=data.response_json_path or preset.get("response_json_path", "choices[0].message.content"),
        temperature=data.temperature,
        max_tokens=data.max_tokens,
        timeout_seconds=data.timeout_seconds,
        rate_limit_rpm=data.rate_limit_rpm,
        tags=data.tags,
        environment=data.environment,
        region=data.region,
        is_shadow=data.is_shadow,
    )
    db.add(conn)
    await db.flush()
    await log_audit(db, user.id, user.organization_id, "llm.create", "llm_connection", str(conn.id))
    return conn


@router.get("/{connection_id}", response_model=LLMConnectionResponse)
async def get_connection(connection_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    conn = await db.get(LLMConnection, connection_id)
    if not conn:
        raise HTTPException(404, "Connection not found")
    return conn


@router.patch("/{connection_id}", response_model=LLMConnectionResponse)
async def update_connection(
    connection_id: UUID, data: LLMConnectionUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    conn = await db.get(LLMConnection, connection_id)
    if not conn:
        raise HTTPException(404, "Connection not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "api_key" and value:
            setattr(conn, "api_key_encrypted", vault.encrypt(value))
        elif field != "api_key":
            setattr(conn, field, value)
    return conn


@router.delete("/{connection_id}")
async def delete_connection(connection_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    conn = await db.get(LLMConnection, connection_id)
    if not conn:
        raise HTTPException(404, "Connection not found")
    conn.is_active = False
    return {"status": "deleted"}


@router.post("/{connection_id}/test")
async def test_connection(connection_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    conn = await db.get(LLMConnection, connection_id)
    if not conn:
        raise HTTPException(404, "Connection not found")
    client = LLMClient({
        "provider": conn.provider,
        "api_key_encrypted": conn.api_key_encrypted,
        "api_base_url": conn.api_base_url,
        "model_name": conn.model_name,
        "custom_headers": conn.custom_headers,
        "response_json_path": conn.response_json_path,
        "temperature": conn.temperature,
        "max_tokens": 50,
        "timeout_seconds": conn.timeout_seconds,
    })
    healthy, message = await client.health_check()
    from datetime import datetime, timezone
    conn.health_status = "healthy" if healthy else "failed"
    conn.last_health_check = datetime.now(timezone.utc)
    return {"healthy": healthy, "message": message, "status": conn.health_status}


@router.get("/stats/summary")
async def connection_stats(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    from sqlalchemy import func
    q = select(LLMConnection)
    if user.organization_id:
        q = q.where(LLMConnection.organization_id == user.organization_id)
    result = await db.execute(q)
    conns = result.scalars().all()
    return {
        "total_tenants": len(conns),
        "healthy_connections": sum(1 for c in conns if c.health_status == "healthy"),
        "failed_connections": sum(1 for c in conns if c.health_status == "failed"),
        "token_usage": sum(c.token_usage_total for c in conns),
    }
