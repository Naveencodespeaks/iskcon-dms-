"""
ORM model for Jobs/Tickets.

Jobs (or tickets) represent units of work that need to be performed.
Each job belongs to a tenant and is linked to a customer.  Jobs have
statuses, types and priorities and can be assigned to an agent.
SLA information can be stored in a separate table; for simplicity
``sla_id`` references a future SLA model.
"""

from __future__ import annotations

import uuid
from enum import Enum

from sqlalchemy import Column, String, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class JobStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ESCALATED = "escalated"


class JobPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class JobType(str, Enum):
    GENERAL = "general"
    SERVICE = "service"
    CLAIM = "claim"
    DELIVERY = "delivery"


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    tenant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    customer_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True
    )
    status: JobStatus = Column(
        SAEnum(JobStatus, name="job_status_enum"), default=JobStatus.OPEN, nullable=False
    )
    type: JobType = Column(
        SAEnum(JobType, name="job_type_enum"), default=JobType.GENERAL, nullable=False
    )
    priority: JobPriority = Column(
        SAEnum(JobPriority, name="job_priority_enum"), default=JobPriority.MEDIUM, nullable=False
    )
    sla_id: uuid.UUID | None = Column(
        UUID(as_uuid=True), nullable=True
    )
    assigned_agent_id: uuid.UUID | None = Column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True
    )
    title: str = Column(String(255), nullable=False)
    description: str | None = Column(String(1024), nullable=True)

    tenant = relationship("Tenant", back_populates="jobs")
    customer = relationship("Customer", back_populates="jobs")
    assigned_agent = relationship("Agent", foreign_keys=[assigned_agent_id])
    assignments = relationship("Assignment", back_populates="job")
    messages = relationship("Message", back_populates="job")
    workflow_state = relationship(
        "WorkflowState", back_populates="job", uselist=False, cascade="all, delete-orphan"
    )
    events = relationship("Event", back_populates="job", cascade="all, delete-orphan")
    escalations = relationship("Escalation", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Job id={self.id} status={self.status} type={self.type}>"