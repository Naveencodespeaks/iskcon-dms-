"""
ORM model for external Integrations.

Integrations store credentials for third party services such as
WhatsApp, Slack, CRM or ERP systems.  Credentials should be
encrypted at rest; however this model stores them in JSON for
illustration.  In production, integrate with a secrets manager and
encrypt sensitive data.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Integration(TimestampMixin, Base):
    __tablename__ = "integrations"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    tenant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    type: str = Column(String(50), nullable=False)
    credentials: dict | None = Column(JSON, nullable=True)

    tenant = relationship("Tenant")

    def __repr__(self) -> str:
        return f"<Integration id={self.id} type={self.type}>"