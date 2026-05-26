from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


async def log_audit(
    db: AsyncSession,
    user_id: Optional[UUID],
    organization_id: Optional[UUID],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    severity: str = "info",
    ip_address: Optional[str] = None,
):
    entry = AuditLog(
        user_id=user_id,
        organization_id=organization_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        severity=severity,
        ip_address=ip_address,
    )
    db.add(entry)
