from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.data.scan_suites import STATIC_SUITES, DYNAMIC_SUITE_IDS
from app.models.scan import Scan, ProbeResult
from app.models.llm_connection import LLMConnection
from app.models.user import User
from app.schemas.scan import ScanCreate, ScanResponse, SuiteInfo, ProbeResultResponse
from app.services.scan_executor import generate_scan_id
from app.workers.tasks import run_scan_task
from app.services.audit import log_audit

router = APIRouter(prefix="/scans", tags=["scans"])


@router.get("/suites", response_model=list[SuiteInfo])
async def list_suites():
    return [
        SuiteInfo(
            id=s.id, name=s.name, group=s.group, description=s.description,
            severity=s.severity, tags=s.tags, probe_count=s.probe_count,
        )
        for s in STATIC_SUITES
    ]


@router.get("/dynamic-suites")
async def list_dynamic_suites():
    return [{"id": s, "name": s.replace("_", " ").title(), "probes_per_run": 20} for s in DYNAMIC_SUITE_IDS]


@router.get("", response_model=list[ScanResponse])
async def list_scans(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    search: str | None = None,
    status: str | None = None,
    limit: int = Query(50, le=200),
):
    q = select(Scan).order_by(Scan.created_at.desc()).limit(limit)
    if user.organization_id:
        q = q.where(Scan.organization_id == user.organization_id)
    if status:
        q = q.where(Scan.status == status)
    result = await db.execute(q)
    scans = result.scalars().all()
    responses = []
    for s in scans:
        conn = await db.get(LLMConnection, s.llm_connection_id)
        responses.append(ScanResponse(
            id=s.id, scan_id=s.scan_id, llm_connection_id=s.llm_connection_id,
            status=s.status, suites=s.suites, dynamic_suites=s.dynamic_suites,
            total_probes=s.total_probes, passed_probes=s.passed_probes,
            failed_probes=s.failed_probes, security_score=s.security_score,
            risk_score=s.risk_score, vulnerabilities_count=s.vulnerabilities_count,
            duration_seconds=s.duration_seconds, started_at=s.started_at,
            completed_at=s.completed_at, created_at=s.created_at,
            model_name=conn.model_name if conn else None,
            provider=conn.provider if conn else None,
        ))
    return responses


@router.post("", response_model=ScanResponse)
async def start_scan(data: ScanCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    conn = await db.get(LLMConnection, data.llm_connection_id)
    if not conn:
        raise HTTPException(404, "LLM connection not found")

    scan = Scan(
        scan_id=generate_scan_id(),
        organization_id=user.organization_id or conn.organization_id,
        llm_connection_id=data.llm_connection_id,
        status="queued",
        suites=data.suites,
        dynamic_suites=data.dynamic_suites,
        severity_threshold=data.severity_threshold,
        parallelism=data.parallelism,
        scan_depth=data.scan_depth,
    )
    db.add(scan)
    await db.flush()

    task = run_scan_task.delay(str(scan.id), data.suites, data.dynamic_suites, data.parallelism)
    scan.celery_task_id = task.id
    scan.status = "queued"
    await log_audit(db, user.id, user.organization_id, "scan.start", "scan", scan.scan_id)

    return ScanResponse(
        id=scan.id, scan_id=scan.scan_id, llm_connection_id=scan.llm_connection_id,
        status=scan.status, suites=scan.suites, dynamic_suites=scan.dynamic_suites,
        total_probes=0, passed_probes=0, failed_probes=0, security_score=0,
        risk_score=0, vulnerabilities_count=0, duration_seconds=None,
        started_at=None, completed_at=None, created_at=scan.created_at,
        model_name=conn.model_name, provider=conn.provider,
    )


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Scan).where(Scan.scan_id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(404, "Scan not found")
    conn = await db.get(LLMConnection, scan.llm_connection_id)
    return ScanResponse(
        id=scan.id, scan_id=scan.scan_id, llm_connection_id=scan.llm_connection_id,
        status=scan.status, suites=scan.suites, dynamic_suites=scan.dynamic_suites,
        total_probes=scan.total_probes, passed_probes=scan.passed_probes,
        failed_probes=scan.failed_probes, security_score=scan.security_score,
        risk_score=scan.risk_score, vulnerabilities_count=scan.vulnerabilities_count,
        duration_seconds=scan.duration_seconds, started_at=scan.started_at,
        completed_at=scan.completed_at, created_at=scan.created_at,
        model_name=conn.model_name if conn else None, provider=conn.provider if conn else None,
    )


@router.get("/{scan_id}/probes", response_model=list[ProbeResultResponse])
async def get_scan_probes(scan_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Scan).where(Scan.scan_id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(404, "Scan not found")
    probes = await db.execute(select(ProbeResult).where(ProbeResult.scan_id == scan.id))
    return probes.scalars().all()


@router.delete("/{scan_id}")
async def delete_scan(scan_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Scan).where(Scan.scan_id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(404, "Scan not found")
    await db.delete(scan)
    return {"status": "deleted"}
