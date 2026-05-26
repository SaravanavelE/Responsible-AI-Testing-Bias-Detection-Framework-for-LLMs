from fastapi import APIRouter

from app.api.v1 import auth, dashboard, llm_connections, scans, policies, reports, tenants, audit

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(llm_connections.router)
api_router.include_router(scans.router)
api_router.include_router(policies.router)
api_router.include_router(reports.router)
api_router.include_router(tenants.router)
api_router.include_router(audit.router)
