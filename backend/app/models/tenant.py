import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrganizationTenant(Base):
    __tablename__ = "organization_tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(64), default="enterprise")
    region: Mapped[str] = mapped_column(String(64), default="us-east-1")
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    compliance_mode: Mapped[str] = mapped_column(String(64), default="standard")
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    llm_connections: Mapped[list["LLMConnection"]] = relationship(back_populates="organization")
    policies: Mapped[list["Policy"]] = relationship(back_populates="organization")
    scans: Mapped[list["Scan"]] = relationship(back_populates="organization")
