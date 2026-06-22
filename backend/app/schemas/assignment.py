"""
Pydantic schemas for assignments.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel

from ..models.assignment import AssignmentStatus


class AssignmentCreate(BaseModel):
    job_id: uuid.UUID
    agent_id: uuid.UUID


class AssignmentRead(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    agent_id: uuid.UUID
    status: AssignmentStatus

    class Config:
        orm_mode = True