from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permission, get_db
from app.models.tenant import OrganizationTenant
from app.models.user import User

router = APIRouter(prefix="/tenants", tags=["tenants"])


class TenantCreate(BaseModel):
    name: str
    slug: str
    plan: str = "enterprise"
    region: str = "us-east-1"
    compliance_mode: str = "standard"


class TenantResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    plan: str
    region: str
    compliance_mode: str
    is_active: bool

    class Config:
        from_attributes = True


@router.get("", response_model=list[TenantResponse])
async def list_tenants(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("tenants.read")),
):
    result = await db.execute(select(OrganizationTenant).where(OrganizationTenant.is_active == True))
    return result.scalars().all()


@router.post("", response_model=TenantResponse)
async def create_tenant(
    data: TenantCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("tenants.write")),
):
    tenant = OrganizationTenant(**data.model_dump())
    db.add(tenant)
    await db.flush()
    return tenant
