import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LLMConnection(Base):
    __tablename__ = "llm_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organization_tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    api_key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    api_base_url: Mapped[str] = mapped_column(String(512), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    custom_headers: Mapped[dict] = mapped_column(JSONB, default=dict)
    response_json_path: Mapped[str] = mapped_column(String(256), default="response.choices[0].message.content")
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=60)
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, default=60)
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    environment: Mapped[str] = mapped_column(String(32), default="production")
    region: Mapped[str] = mapped_column(String(64), default="us-east-1")
    health_status: Mapped[str] = mapped_column(String(32), default="unknown")
    last_health_check: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    token_usage_total: Mapped[int] = mapped_column(Integer, default=0)
    is_shadow: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    organization: Mapped["OrganizationTenant"] = relationship(back_populates="llm_connections")
    scans: Mapped[list["Scan"]] = relationship(back_populates="llm_connection")
