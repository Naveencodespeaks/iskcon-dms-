"""
Job (ticket) API endpoints.

These endpoints allow clients to create, retrieve, list and update
jobs (also referred to as tickets).  Jobs are scoped to a tenant and
represent units of work that need to be completed.  Permission checks
ensure that only authorized users may perform modifications.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...schemas.job import JobCreate, JobRead, JobUpdate
from ...services.job_service import create_job, get_job, list_jobs, update_job
from ...auth.dependencies import get_current_tenant_id
from ...rbac.dependencies import permission_required


router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("/", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_job_endpoint(
    job_in: JobCreate,
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("jobs:create"),
) -> JobRead:
    """Create a new job for the current tenant.

    Requires the ``jobs:create`` permission.  The ``tenant_id`` field in
    ``job_in`` must match the tenant_id of the authenticated user (enforced by
    the JWT claims and permission dependency in real deployments).
    """
    job = await create_job(session, job_in)
    return job


@router.get("/", response_model=List[JobRead])
async def list_jobs_endpoint(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("jobs:view"),
) -> List[JobRead]:
    """List jobs for the current tenant.

    You can optionally filter by status, provide pagination via ``skip`` and
    ``limit``.  Requires ``jobs:view`` permission.
    """
    # Convert status string to JobStatus enum if provided
    from ...models.job import JobStatus
    status_enum: Optional[JobStatus] = None
    if status:
        try:
            status_enum = JobStatus(status)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status filter")
    jobs = await list_jobs(session, tenant_id=tenant_id, status=status_enum, skip=skip, limit=limit)
    return jobs


@router.get("/{job_id}", response_model=JobRead)
async def get_job_endpoint(
    job_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("jobs:view"),
) -> JobRead:
    """Retrieve a single job by ID."""
    job = await get_job(session, tenant_id=tenant_id, job_id=str(job_id))
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.patch("/{job_id}", response_model=JobRead)
async def update_job_endpoint(
    job_id: uuid.UUID,
    job_in: JobUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("jobs:update"),
) -> JobRead:
    """Update a job's fields (status, priority, assignment)."""
    job = await get_job(session, tenant_id=tenant_id, job_id=str(job_id))
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    updated = await update_job(session, job, job_in)
    return updated