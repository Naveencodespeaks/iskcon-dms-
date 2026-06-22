"""
ORM model for Escalations.

Escalations track when an issue has been raised for a job due to an
exception (e.g., SLA breach, negative sentiment).  Escalations can
require human intervention and must be resolved before a job can
continue.  The ``trigger`` describes why the escalation occurred.
"""

from __future__ import annotations

import uuid
from enum import Enum

from sqlalchemy import Column, String, Enum as SAEnum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class EscalationStatus(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"


class Escalation(TimestampMixin, Base):
    __tablename__ = "escalations"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    job_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    trigger: str = Column(String(255), nullable=False)
    raised_by: uuid.UUID | None = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: EscalationStatus = Column(
        SAEnum(EscalationStatus, name="escalation_status_enum"), default=EscalationStatus.PENDING, nullable=False
    )
    created_at: DateTime = Column(DateTime(timezone=True), nullable=False)

    job = relationship("Job", back_populates="escalations")
    raiser = relationship("User")

    def __repr__(self) -> str:
        return f"<Escalation id={self.id} trigger={self.trigger} status={self.status}>"