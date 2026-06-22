"""
Celery tasks for assignment engine.

This module defines tasks that scan for unassigned jobs and allocate
them to agents based on a simple load‑balancing rule (least current
load).  In a production deployment, this logic would incorporate
skills, locations, and SLA requirements.  The task is intended to be
scheduled periodically via Celery beat.
"""

from __future__ import annotations

import asyncio
import datetime as dt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import AsyncSessionLocal
from ..core.celery_app import celery_app
from ..models.job import Job
from ..models.agent import Agent
from ..services.assignment_service import assign_job


@celery_app.task
def assign_unassigned_jobs():
    """Celery task to assign unassigned jobs to available agents.

    This function opens its own asynchronous SQLAlchemy session,
    queries for jobs without assigned agents, then picks the agent with
    the lowest current_load for the same tenant and assigns the job.
    """
    async def _run():
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            # Find unassigned jobs
            result = await session.execute(select(Job).where(Job.assigned_agent_id.is_(None)))
            jobs = result.scalars().all()
            for job in jobs:
                # Find available agent in tenant
                agent_result = await session.execute(
                    select(Agent).where(Agent.tenant_id == job.tenant_id).order_by(Agent.current_load.asc())
                )
                agent = agent_result.scalars().first()
                if agent:
                    await assign_job(session, job, agent)
    # Run the async logic within the event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_run())