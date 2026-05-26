from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.report import Report
from app.models.user import User
from app.workers.tasks import generate_report_task

router = APIRouter(prefix="/reports", tags=["reports"])

REPORT_TYPES = {
    "executive": [
        "Executive Summary", "Risk Posture Brief", "Board / Investor Report", "Cyber-Liability Disclosure"
    ],
    "compliance": [
        "OWASP LLM Top 10 Audit", "NIST AI RMF Mapping", "EU AI Act Report", "ISO 42001",
        "ISO 27001", "SOC 2 AI Supplement", "HIPAA", "GDPR DPIA", "PCI-DSS", "MITRE ATLAS", "CERT-In LLM Audit"
    ],
    "technical": ["Technical Deep-Dive", "Red-Team Playbook", "Remediation Playbook", "Model Card"],
    "audience": ["Customer Trust Report", "Vendor Assessment Response", "Developer Brief"],
}


class ReportCreate(BaseModel):
    report_type: str
    scan_id: UUID | None = None
    audience: str = "technical"
    title: str | None = None


@router.get("/types")
async def list_report_types():
    return REPORT_TYPES


@router.get("")
async def list_reports(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    q = select(Report).order_by(Report.created_at.desc())
    if user.organization_id:
        q = q.where(Report.organization_id == user.organization_id)
    result = await db.execute(q.limit(50))
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "report_type": r.report_type,
            "status": r.status,
            "s3_key": r.s3_key,
            "created_at": r.created_at.isoformat(),
        }
        for r in result.scalars().all()
    ]


@router.post("")
async def generate_report(data: ReportCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    report = Report(
        organization_id=user.organization_id or UUID("00000000-0000-0000-0000-000000000001"),
        scan_id=data.scan_id,
        report_type=data.report_type,
        audience=data.audience,
        title=data.title or f"{data.report_type} Report",
        created_by=user.id,
        status="generating",
    )
    db.add(report)
    await db.flush()
    generate_report_task.delay(str(report.id))
    return {"id": str(report.id), "status": "generating", "title": report.title}


@router.get("/{report_id}")
async def get_report(report_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    report = await db.get(Report, report_id)
    if not report:
        from fastapi import HTTPException
        raise HTTPException(404, "Report not found")
    return {
        "id": str(report.id),
        "title": report.title,
        "status": report.status,
        "html_content": report.html_content,
        "s3_key": report.s3_key,
        "metadata": report.report_metadata,
    }
