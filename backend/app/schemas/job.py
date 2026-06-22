"""
Pydantic schemas for jobs.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field

from ..models.job import JobStatus, JobPriority, JobType


class JobBase(BaseModel):
    title: str = Field(..., description="Short title of the job")
    description: Optional[str] = Field(None, description="Detailed description of the job")
    type: JobType = Field(JobType.GENERAL, description="Type of the job")
    priority: JobPriority = Field(JobPriority.MEDIUM, description="Priority of the job")
    customer_id: Optional[uuid.UUID] = None


class JobCreate(JobBase):
    tenant_id: uuid.UUID


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[JobStatus] = None
    priority: Optional[JobPriority] = None
    assigned_agent_id: Optional[uuid.UUID] = None


class JobRead(JobBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    status: JobStatus
    assigned_agent_id: Optional[uuid.UUID] = None

    class Config:
        orm_mode = True