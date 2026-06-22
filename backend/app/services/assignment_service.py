"""
Service layer for managing job assignments.

This module encapsulates the logic for assigning jobs to agents,
creating assignment records and updating job/agent state.  It also
allows listing assignments and updating statuses.
"""

from __future__ import annotations

import datetime as dt
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.assignment import Assignment, AssignmentStatus
from ..models.agent import Agent
from ..models.job import Job


async def assign_job(session: AsyncSession, job: Job, agent: Agent) -> Assignment:
    """Assign a job to an agent.

    Creates an Assignment record, updates the job's assigned_agent_id and
    increments the agent's current load.  All changes are committed
    atomically within the same transaction.
    """
    # Create assignment record
    assignment = Assignment(
        job_id=job.id,
        agent_id=agent.id,
        assigned_at=dt.datetime.utcnow(),
        status=AssignmentStatus.ACTIVE,
    )
    job.assigned_agent_id = agent.id
    agent.current_load = agent.current_load + 1
    session.add_all([assignment, job, agent])
    await session.commit()
    await session.refresh(assignment)
    return assignment


async def list_assignments(session: AsyncSession, job_id: Optional[str] = None) -> List[Assignment]:
    """List assignments, optionally filtered by job."""
    stmt = select(Assignment)
    if job_id:
        stmt = stmt.where(Assignment.job_id == job_id)
    result = await session.execute(stmt)
    return result.scalars().all()