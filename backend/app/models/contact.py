"""
ORM model for Contact handles.

Contacts link customers to communication channels such as WhatsApp,
email or SMS.  A customer may have multiple contacts; one can be
marked as primary for preferred communication.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Contact(TimestampMixin, Base):
    __tablename__ = "contacts"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    customer_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    channel: str = Column(String(50), nullable=False)  # e.g., "whatsapp", "email"
    handle: str = Column(String(255), nullable=False)  # e.g., phone number or email
    is_primary: bool = Column(Boolean, default=False, nullable=False)

    customer = relationship("Customer", back_populates="contacts")

    def __repr__(self) -> str:
        return f"<Contact id={self.id} channel={self.channel} handle={self.handle}>"