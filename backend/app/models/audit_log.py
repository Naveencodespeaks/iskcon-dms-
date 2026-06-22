"""
ORM model for Audit Logs.

Audit logs provide an immutable record of all actions taken by users
and agents within the platform.  Each log entry records who
performed the action, what resource was affected, the type of action
and any additional details.  Use this table to meet compliance
requirements and support debugging.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    tenant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    user_id: uuid.UUID | None = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: str = Column(String(100), nullable=False)
    resource: str = Column(String(255), nullable=False)
    timestamp: DateTime = Column(DateTime(timezone=True), nullable=False)
    details: dict | None = Column(JSON, nullable=True)

    tenant = relationship("Tenant")
    user = relationship("User")

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action} resource={self.resource}>"