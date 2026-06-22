"""
Service layer for job/ticket operations.

The job service encapsulates business logic for creating, listing,
updating and retrieving jobs.  All operations respect tenant
isolation by filtering on ``tenant_id``.  Use these helpers in API
routes instead of writing raw queries in controllers.
"""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.job import Job, JobStatus, JobPriority, JobType
from ..schemas.job import JobCreate, JobUpdate


async def create_job(session: AsyncSession, job_in: JobCreate) -> Job:
    """Create a new job for the given tenant.

    Parameters
    ----------
    session: AsyncSession
        Database session.
    job_in: JobCreate
        Pydantic model containing job attributes.

    Returns
    -------
    Job
        Newly created job ORM instance.
    """
    job = Job(
        tenant_id=job_in.tenant_id,
        customer_id=job_in.customer_id,
        title=job_in.title,
        description=job_in.description,
        type=job_in.type,
        priority=job_in.priority,
        status=JobStatus.OPEN,
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job


async def get_job(session: AsyncSession, tenant_id: str, job_id: str) -> Optional[Job]:
    """Retrieve a job by ID ensuring it belongs to the tenant."""
    stmt = select(Job).where(Job.id == job_id, Job.tenant_id == tenant_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def list_jobs(
    session: AsyncSession,
    tenant_id: str,
    status: Optional[JobStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Job]:
    """List jobs for a tenant with optional filtering by status."""
    stmt = select(Job).where(Job.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(Job.status == status)
    stmt = stmt.offset(skip).limit(limit).order_by(Job.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_job(session: AsyncSession, job: Job, job_in: JobUpdate) -> Job:
    """Update fields on a job."""
    for field, value in job_in.dict(exclude_unset=True).items():
        setattr(job, field, value)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job