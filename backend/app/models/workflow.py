"""
ORM model for WorkflowState.

Each job is associated with a persistent state machine.  The
WorkflowState table tracks the current state and a JSON context of
variables used by the workflow engine.  ``last_transition_at`` records
the timestamp of the last state transition.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class WorkflowState(TimestampMixin, Base):
    __tablename__ = "workflow_states"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    job_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    current_state: str = Column(String(100), nullable=False)
    context: dict | None = Column(JSON, nullable=True)
    last_transition_at: DateTime = Column(DateTime(timezone=True), nullable=True)

    job = relationship("Job", back_populates="workflow_state")

    def __repr__(self) -> str:
        return f"<WorkflowState job_id={self.job_id} state={self.current_state}>"