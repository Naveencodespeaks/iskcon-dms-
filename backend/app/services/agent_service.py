"""
Agent orchestration service.

This service coordinates the various agents (assignment, communication,
escalation, etc.) through a simple event bus.  In a full
implementation, agents would communicate via Redis streams and Celery
workers.  Here we provide a minimal synchronous stub that executes
agent logic directly for demonstration purposes.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from .job_service import list_jobs
from .assignment_service import assign_job
from .messaging_service import send_outbound_message
from ..models.job import Job, JobStatus
from ..models.agent import Agent


async def process_inbound_message(session: AsyncSession, job: Job, message: Dict[str, Any]) -> None:
    """Entry point invoked when a new message arrives for a job.

    This function demonstrates how the coordinator might invoke the
    assignment agent and communication agent.  For example, if a new
    job arrives and has no assigned agent, the assignment agent is
    invoked; otherwise, messages are routed to the communication agent.
    """
    # If job is unassigned, assign to an available agent (demo uses first agent)
    if job.assigned_agent_id is None:
        # naive assignment: pick first available agent in the tenant
        result = await session.execute(
            "SELECT * FROM agents WHERE tenant_id = :tenant_id ORDER BY current_load LIMIT 1",
            {"tenant_id": str(job.tenant_id)},
        )
        agent_row = result.first()
        if agent_row:
            agent = agent_row[0]
            await assign_job(session, job, agent)
    # Send an automated acknowledgement via communication agent
    from ..schemas.message import MessageOutbound

    outbound_msg = MessageOutbound(
        job_id=job.id,
        channel="whatsapp",
        content="Thank you for your message. Our team will respond shortly.",
        extra_metadata={},
    )
    await send_outbound_message(session, outbound_msg)