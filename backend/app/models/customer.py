"""
ORM model for Customers.

Customers represent the end‑users or clients served by the tenant.
Contact information and metadata are stored in JSONB columns for
flexibility.  Each customer can have multiple contact handles (e.g.,
WhatsApp numbers) stored in the Contact model.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    tenant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: str = Column(String(255), nullable=False)
    contact_info: dict | None = Column(JSON, nullable=True)
    extra_metadata: dict | None = Column(JSON, nullable=True)

    tenant = relationship("Tenant", back_populates="customers")
    contacts = relationship(
        "Contact", back_populates="customer", cascade="all, delete-orphan"
    )
    jobs = relationship("Job", back_populates="customer")

    def __repr__(self) -> str:
        return f"<Customer id={self.id} name={self.name}>"