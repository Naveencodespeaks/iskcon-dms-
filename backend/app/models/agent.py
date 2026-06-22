"""
ORM model for Agents.

Agents represent human operators or field workers.  Each agent is
associated with a User account and belongs to a tenant.  Agents can
declare their skills in a JSON column to aid assignment logic.  The
current_load field tracks how many jobs are presently assigned.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Agent(TimestampMixin, Base):
    __tablename__ = "agents"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    tenant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    user_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    skills: dict | None = Column(JSON, nullable=True)
    current_load: int = Column(Integer, default=0, nullable=False)

    tenant = relationship("Tenant")
    user = relationship("User", back_populates="agent")
    assignments = relationship("Assignment", back_populates="agent")

    def __repr__(self) -> str:
        return f"<Agent id={self.id} user_id={self.user_id}>"