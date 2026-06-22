"""
Escalation API endpoints.

Escalations are raised when something goes wrong with a job and need
human or supervisor intervention.  These endpoints allow listing
escalations for a tenant, creating a new escalation and resolving
existing ones.
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...models.escalation import Escalation, EscalationStatus
from ...models.job import Job
from ...schemas.escalation import EscalationCreate, EscalationRead
from ...auth.dependencies import get_current_active_user, get_current_tenant_id
from ...rbac.dependencies import permission_required


router = APIRouter(prefix="/api/v1/escalations", tags=["escalations"])


@router.get("/", response_model=List[EscalationRead])
async def list_escalations(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("escalations:view"),
) -> List[Escalation]:
    """List escalations for the current tenant."""
    result = await session.execute(select(Escalation).join(Job).where(Job.tenant_id == tenant_id))
    return result.scalars().all()


@router.post("/", response_model=EscalationRead, status_code=status.HTTP_201_CREATED)
async def create_escalation(
    esc_in: EscalationCreate,
    current_user = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("escalations:create"),
) -> Escalation:
    """Create a new escalation for a job."""
    job = await session.get(Job, esc_in.job_id)
    if not job or job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    escalation = Escalation(
        job_id=esc_in.job_id,
        trigger=esc_in.trigger,
        raised_by=current_user.id,
        status=EscalationStatus.PENDING,
    )
    session.add(escalation)
    await session.commit()
    await session.refresh(escalation)
    return escalation


@router.patch("/{escalation_id}", response_model=EscalationRead)
async def resolve_escalation(
    escalation_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("escalations:update"),
) -> Escalation:
    """Resolve an escalation (mark status as RESOLVED)."""
    escalation = await session.get(Escalation, escalation_id)
    if not escalation or escalation.job.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escalation not found")
    escalation.status = EscalationStatus.RESOLVED
    session.add(escalation)
    await session.commit()
    await session.refresh(escalation)
    return escalation