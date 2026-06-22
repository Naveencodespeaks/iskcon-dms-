"""
ORM model for permissions.

Permissions define an action that can be performed in the system.  They
are identified by a unique code (e.g., ``jobs:create``, ``users:manage``)
and have a human readable description.  Permissions are assigned to
roles via the RolePermissions association table.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class Permission(Base):
    __tablename__ = "permissions"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    code: str = Column(String(100), unique=True, nullable=False)
    description: str | None = Column(String(255), nullable=True)

    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
    )

    def __repr__(self) -> str:
        return f"<Permission code={self.code}>"