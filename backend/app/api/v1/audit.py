from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.audit import AuditLog
from app.models.user import User

router = APIRouter(prefix="/audit-logs", tags=["audit"])


@router.get("")
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    action: str | None = None,
    limit: int = Query(100, le=500),
):
    q = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if user.organization_id:
        q = q.where(AuditLog.organization_id == user.organization_id)
    if action:
        q = q.where(AuditLog.action.contains(action))
    result = await db.execute(q)
    return [
        {
            "id": str(a.id),
            "action": a.action,
            "resource_type": a.resource_type,
            "resource_id": a.resource_id,
            "severity": a.severity,
            "details": a.details,
            "ip_address": a.ip_address,
            "created_at": a.created_at.isoformat(),
        }
        for a in result.scalars().all()
    ]
