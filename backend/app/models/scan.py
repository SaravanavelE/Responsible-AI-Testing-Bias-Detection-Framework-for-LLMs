import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("organization_tenants.id"), nullable=False)
    llm_connection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("llm_connections.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    suites: Mapped[list] = mapped_column(JSONB, default=list)
    dynamic_suites: Mapped[list] = mapped_column(JSONB, default=list)
    severity_threshold: Mapped[str] = mapped_column(String(16), default="low")
    parallelism: Mapped[int] = mapped_column(Integer, default=4)
    scan_depth: Mapped[str] = mapped_column(String(32), default="standard")
    total_probes: Mapped[int] = mapped_column(Integer, default=0)
    passed_probes: Mapped[int] = mapped_column(Integer, default=0)
    failed_probes: Mapped[int] = mapped_column(Integer, default=0)
    security_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    vulnerabilities_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    celery_task_id: Mapped[Optional[str]] = mapped_column(String(128))
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    scan_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    organization: Mapped["OrganizationTenant"] = relationship(back_populates="scans")
    llm_connection: Mapped["LLMConnection"] = relationship(back_populates="scans")
    probe_results: Mapped[list["ProbeResult"]] = relationship(back_populates="scan", cascade="all, delete-orphan")


class ProbeResult(Base):
    __tablename__ = "probe_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    probe_name: Mapped[str] = mapped_column(String(255), nullable=False)
    probe_category: Mapped[str] = mapped_column(String(128), nullable=False)
    suite: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="medium")
    status: Mapped[str] = mapped_column(String(32), default="pending")
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[Optional[str]] = mapped_column(Text)
    detection_type: Mapped[Optional[str]] = mapped_column(String(128))
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    evidence: Mapped[dict] = mapped_column(JSONB, default=dict)
    compliance_mappings: Mapped[list] = mapped_column(JSONB, default=list)
    recommendations: Mapped[list] = mapped_column(JSONB, default=list)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    scan: Mapped[Scan] = relationship(back_populates="probe_results")


class DynamicProbe(Base):
    __tablename__ = "dynamic_probes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suite: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), default="high")
    probe_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    scan_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("scans.id"))
