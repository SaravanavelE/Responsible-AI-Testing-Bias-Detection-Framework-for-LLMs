import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organization_tenants.id"), nullable=False)
    llm_connection_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("llm_connections.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    allowed_tools: Mapped[list] = mapped_column(JSONB, default=list)
    forbidden_phrases: Mapped[list] = mapped_column(JSONB, default=list)
    allowed_domains: Mapped[list] = mapped_column(JSONB, default=list)
    max_token_budget: Mapped[int] = mapped_column(Integer, default=100000)
    allowed_providers: Mapped[list] = mapped_column(JSONB, default=list)
    pii_policy: Mapped[str] = mapped_column(String(32), default="redact")
    prompt_length_limit: Mapped[int] = mapped_column(Integer, default=32000)
    compliance_mode: Mapped[str] = mapped_column(String(64), default="standard")
    custom_regex_patterns: Mapped[list] = mapped_column(JSONB, default=list)
    default_action: Mapped[str] = mapped_column(String(32), default="warn")
    rules: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    organization: Mapped["OrganizationTenant"] = relationship(back_populates="policies")
