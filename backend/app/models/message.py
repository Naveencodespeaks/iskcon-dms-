"""
ORM model for Messages/Conversations.

Messages represent communication between customers and the system.  A
message belongs to a job and may be inbound (from customer) or
outbound (from agent or automated system).  The sender_id field
refers to a User when the message originates from an agent; inbound
messages from WhatsApp may leave sender_id null and record the
customer contact in metadata.  Additional metadata may contain
information such as message type (text, image) or WhatsApp specific
fields.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Message(TimestampMixin, Base):
    __tablename__ = "messages"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    tenant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    job_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True
    )
    sender_id: Optional[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    channel: str = Column(String(50), nullable=False)  # e.g., "whatsapp"
    content: str = Column(String(4096), nullable=False)
    extra_metadata: dict | None = Column(JSON, nullable=True)
    timestamp: DateTime = Column(DateTime(timezone=True), nullable=False)

    job = relationship("Job", back_populates="messages")
    sender = relationship("User")

    def __repr__(self) -> str:
        return f"<Message id={self.id} job_id={self.job_id}>"