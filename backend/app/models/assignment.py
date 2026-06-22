"""
ORM model for Assignment history.

Assignments record the history of which agent was assigned to a job and
when.  The status tracks whether the assignment is active, completed
or cancelled.  Multiple assignments can exist per job over time.
"""

from __future__ import annotations

import uuid
from enum import Enum

from sqlalchemy import Column, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class AssignmentStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Assignment(TimestampMixin, Base):
    __tablename__ = "assignments"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    job_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    agent_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    assigned_at: DateTime = Column(DateTime(timezone=True), nullable=False)
    status: AssignmentStatus = Column(
        SAEnum(AssignmentStatus, name="assignment_status_enum"), default=AssignmentStatus.PENDING, nullable=False
    )

    job = relationship("Job", back_populates="assignments")
    agent = relationship("Agent", back_populates="assignments")

    def __repr__(self) -> str:
        return f"<Assignment job_id={self.job_id} agent_id={self.agent_id} status={self.status}>"