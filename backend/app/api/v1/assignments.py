"""
Assignment endpoints.

This router exposes endpoints to list and create job assignments.
Assignments link jobs to agents and track assignment status over time.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...models.assignment import Assignment
from ...models.job import Job
from ...models.agent import Agent
from ...schemas.assignment import AssignmentCreate, AssignmentRead
from ...auth.dependencies import get_current_tenant_id
from ...rbac.dependencies import permission_required
from ...services.assignment_service import assign_job, list_assignments

router = APIRouter(prefix="/api/v1/assignments", tags=["assignments"])


@router.get("/", response_model=List[AssignmentRead])
async def list_assignments_endpoint(
    job_id: Optional[uuid.UUID] = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("assignments:view"),
) -> List[Assignment]:
    """List assignments, optionally filtered by job."""
    assignments = await list_assignments(session, job_id=str(job_id) if job_id else None)
    # Filter by tenant: ensure job belongs to tenant
    filtered = []
    for assignment in assignments:
        if assignment.job.tenant_id == tenant_id:
            filtered.append(assignment)
    return filtered


@router.post("/", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assign_in: AssignmentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("assignments:create"),
) -> Assignment:
    """Assign a job to an agent."""
    job = await session.get(Job, assign_in.job_id)
    agent = await session.get(Agent, assign_in.agent_id)
    if not job or job.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found or unauthorized")
    if not agent or agent.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found or unauthorized")
    assignment = await assign_job(session, job, agent)
    return assignment