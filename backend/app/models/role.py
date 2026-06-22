"""
ORM model for Role definitions.

Roles are scoped to tenants and group permissions.  Users are
assigned a single role for simplicity; however, the RolePermissions
table supports many‑to‑many relationships to permissions.  Each role
defines a set of permissions using codes such as ``jobs:create`` or
``users:manage``.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Role(TimestampMixin, Base):
    __tablename__ = "roles"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    tenant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    name: str = Column(String(100), nullable=False)
    description: str | None = Column(String(255), nullable=True)

    # relationships
    tenant = relationship("Tenant", back_populates="roles")
    users = relationship("User", back_populates="role")
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
    )

    def __repr__(self) -> str:
        return f"<Role id={self.id} name={self.name}>"