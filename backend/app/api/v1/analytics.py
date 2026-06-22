"""
Analytics endpoints (placeholder).

This router exposes endpoints that return operational metrics such as
job counts, SLA breaches and agent workloads.  The current
implementation returns static data for demonstration purposes.  In a
production system, these endpoints would query analytics tables or
aggregate events.
"""

from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_tenant_id
from app.rbac.dependencies import permission_required

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview(
    tenant_id = Depends(get_current_tenant_id),
    _: None = permission_required("analytics:view"),
) -> dict:
    """Return a summary of key metrics."""
    # Dummy data; replace with real analytics queries
    return {
        "total_jobs": 42,
        "open_jobs": 10,
        "completed_jobs": 25,
        "sla_breaches": 3,
    }