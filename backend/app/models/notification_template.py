"""
ORM model for Notification Templates.

Notification templates define the messages sent to users or customers
when certain events occur (e.g., job updates, reminders).  Templates
are stored per tenant and keyed by event_type.  The template can
contain placeholder variables that are resolved at send time.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class NotificationTemplate(TimestampMixin, Base):
    __tablename__ = "notification_templates"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    tenant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    event_type: str = Column(String(100), nullable=False)
    template: str = Column(Text, nullable=False)

    tenant = relationship("Tenant")

    def __repr__(self) -> str:
        return f"<NotificationTemplate id={self.id} event_type={self.event_type}>"