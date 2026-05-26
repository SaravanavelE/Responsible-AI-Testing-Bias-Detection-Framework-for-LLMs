from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ScanCreate(BaseModel):
    llm_connection_id: UUID
    suites: list[str] = []
    dynamic_suites: list[str] = []
    severity_threshold: str = "low"
    parallelism: int = 4
    scan_depth: str = "standard"


class ProbeResultResponse(BaseModel):
    id: UUID
    probe_name: str
    probe_category: str
    suite: str
    severity: str
    status: str
    passed: bool
    detection_type: Optional[str]
    risk_score: float
    duration_ms: Optional[int]

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    id: UUID
    scan_id: str
    llm_connection_id: UUID
    status: str
    suites: list
    dynamic_suites: list
    total_probes: int
    passed_probes: int
    failed_probes: int
    security_score: float
    risk_score: float
    vulnerabilities_count: int
    duration_seconds: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    tenant_name: Optional[str] = None
    model_name: Optional[str] = None
    provider: Optional[str] = None

    class Config:
        from_attributes = True


class SuiteInfo(BaseModel):
    id: str
    name: str
    group: str
    description: str
    severity: str
    tags: list[str]
    probe_count: int
