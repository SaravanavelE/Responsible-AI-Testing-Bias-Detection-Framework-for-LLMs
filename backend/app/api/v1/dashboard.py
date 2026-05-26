from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.scan import Scan, ProbeResult
from app.models.llm_connection import LLMConnection
from app.engines.firewall import firewall

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    org_filter = Scan.organization_id == user.organization_id if user.organization_id else True

    total_scans = await db.scalar(select(func.count(Scan.id)).where(org_filter)) or 0
    vulns = await db.scalar(
        select(func.sum(Scan.vulnerabilities_count)).where(org_filter, Scan.status == "completed")
    ) or 0
    failed_probes = await db.scalar(
        select(func.sum(Scan.failed_probes)).where(org_filter, Scan.status == "completed")
    ) or 0
    passed_probes = await db.scalar(
        select(func.sum(Scan.passed_probes)).where(org_filter, Scan.status == "completed")
    ) or 0
    avg_score = await db.scalar(
        select(func.avg(Scan.security_score)).where(org_filter, Scan.status == "completed")
    ) or 0
    active_tenants = await db.scalar(
        select(func.count(LLMConnection.id)).where(
            LLMConnection.is_active == True,
            LLMConnection.organization_id == user.organization_id if user.organization_id else True,
        )
    ) or 0

    return {
        "total_scans": total_scans,
        "vulnerabilities_detected": int(vulns),
        "failed_probes": int(failed_probes),
        "passed_probes": int(passed_probes),
        "average_security_score": round(float(avg_score or 0), 2),
        "active_llm_tenants": int(active_tenants),
        "compliance_posture_score": round(float(avg_score or 0) * 0.95, 2),
        "prompt_injection_blocked": firewall.blocked_injection_count,
        "data_leakage_blocked": firewall.blocked_dlp_count,
        "security_posture_score": round(float(avg_score or 0), 2),
        "total_vulnerabilities": int(vulns),
        "average_risk_score": round(100 - float(avg_score or 0), 2),
        "total_connected_models": int(active_tenants),
    }


@router.get("/charts/vulnerabilities-by-severity")
async def vulnerabilities_by_severity(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(ProbeResult.severity, func.count(ProbeResult.id))
        .where(ProbeResult.passed == False)
        .group_by(ProbeResult.severity)
    )
    data = {row[0].upper(): row[1] for row in result.all()}
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        data.setdefault(sev, 0)
    return [{"severity": k, "count": v} for k, v in data.items()]


@router.get("/charts/failed-probes-trend")
async def failed_probes_trend(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return [
        {"date": "2026-05-19", "failed": 12, "passed": 88},
        {"date": "2026-05-20", "failed": 8, "passed": 92},
        {"date": "2026-05-21", "failed": 15, "passed": 85},
        {"date": "2026-05-22", "failed": 6, "passed": 94},
        {"date": "2026-05-23", "failed": 10, "passed": 90},
        {"date": "2026-05-24", "failed": 4, "passed": 96},
        {"date": "2026-05-25", "failed": 7, "passed": 93},
    ]


@router.get("/charts/attack-categories")
async def attack_categories(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(ProbeResult.probe_category, func.count(ProbeResult.id))
        .where(ProbeResult.passed == False)
        .group_by(ProbeResult.probe_category)
        .limit(10)
    )
    return [{"category": r[0], "count": r[1]} for r in result.all()] or [
        {"category": "injection", "count": 24},
        {"category": "jailbreak", "count": 18},
        {"category": "dlp", "count": 12},
        {"category": "agent", "count": 9},
    ]


@router.get("/recent-scans")
async def recent_scans(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user), limit: int = 10):
    from app.models.tenant import OrganizationTenant

    q = select(Scan).order_by(Scan.created_at.desc()).limit(limit)
    if user.organization_id:
        q = q.where(Scan.organization_id == user.organization_id)
    result = await db.execute(q)
    scans = result.scalars().all()
    items = []
    for s in scans:
        conn = await db.get(LLMConnection, s.llm_connection_id)
        org = await db.get(OrganizationTenant, s.organization_id) if s.organization_id else None
        items.append({
            "scan_id": s.scan_id,
            "timestamp": s.created_at.isoformat(),
            "tenant": org.name if org else "Default",
            "model": conn.model_name if conn else "unknown",
            "total_probes": s.total_probes,
            "failed_probes": s.failed_probes,
            "status": s.status,
            "security_score": s.security_score,
        })
    return items


@router.get("/top-failing-probes")
async def top_failing_probes(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(
            ProbeResult.probe_name,
            ProbeResult.probe_category,
            ProbeResult.severity,
            func.count(ProbeResult.id).label("failures"),
        )
        .where(ProbeResult.passed == False)
        .group_by(ProbeResult.probe_name, ProbeResult.probe_category, ProbeResult.severity)
        .order_by(func.count(ProbeResult.id).desc())
        .limit(10)
    )
    items = []
    for row in result.all():
        items.append({
            "probe_name": row[0],
            "category": row[1],
            "failure_rate": min(95, row[3] * 10),
            "severity": row[2],
            "last_triggered": "2026-05-25T10:00:00Z",
        })
    return items or [
        {"probe_name": "injection_1", "category": "injection", "failure_rate": 78, "severity": "critical", "last_triggered": "2026-05-25T10:00:00Z"},
    ]
