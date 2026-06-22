"""
ORM model for Tenant entities.

Tenants represent organizations using the platform.  Each tenant has a
unique UUID primary key and may store additional configuration in the
``settings`` JSONB column.  Multi‑tenant isolation is enforced by
scoping queries using tenant_id; ensure that all child models
reference the tenant_id of their owning tenant.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenants"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    name: str = Column(String(255), nullable=False, unique=True)
    slug: str = Column(String(100), nullable=True, unique=True)
    industry: str = Column(String(100), nullable=True)
    settings: dict | None = Column(JSON, nullable=True)

    # relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="tenant", cascade="all, delete-orphan")
    customers = relationship(
        "Customer", back_populates="tenant", cascade="all, delete-orphan"
    )
    jobs = relationship("Job", back_populates="tenant", cascade="all, delete-orphan")
    documents = relationship(
        "Document", back_populates="tenant", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Tenant id={self.id} name={self.name}>"