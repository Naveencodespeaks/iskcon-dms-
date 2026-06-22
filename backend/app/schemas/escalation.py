"""
Pydantic schemas for escalations.

Escalations represent issues raised against jobs (tickets) that require
special attention, such as SLA breaches or negative sentiment.  These
schemas define the shape of data exchanged via the API.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.escalation import EscalationStatus


class EscalationBase(BaseModel):
    job_id: uuid.UUID = Field(..., description="ID of the job that is escalated")
    trigger: str = Field(..., description="Reason the escalation was raised")


class EscalationCreate(EscalationBase):
    pass


class EscalationRead(EscalationBase):
    id: uuid.UUID
    status: EscalationStatus
    created_at: datetime

    class Config:
        orm_mode = True