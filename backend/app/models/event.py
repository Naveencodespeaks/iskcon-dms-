"""
ORM model for Events.

Event records capture the history of actions and state changes for a
job.  Each event has a type (e.g., ``job_created``, ``status_updated``)
and a payload containing event‑specific data.  Events are useful for
replaying workflows and auditing.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Event(TimestampMixin, Base):
    __tablename__ = "events"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    job_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    event_type: str = Column(String(100), nullable=False)
    payload: dict | None = Column(JSON, nullable=True)
    created_at: DateTime = Column(DateTime(timezone=True), nullable=False)

    job = relationship("Job", back_populates="events")

    def __repr__(self) -> str:
        return f"<Event id={self.id} type={self.event_type}>"