"""
ORM model for User accounts.

Users belong to a tenant and may have a role assigned for RBAC.  A
user has a unique email within their tenant.  The password is
securely hashed before storage; never store plaintext passwords.
"""

from __future__ import annotations

import uuid
from enum import Enum

from sqlalchemy import Column, String, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    tenant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    email: str = Column(String(255), nullable=False)
    name: str = Column(String(255), nullable=False)
    password_hash: str = Column(String(255), nullable=False)
    role_id: uuid.UUID | None = Column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )
    status: UserStatusEnum = Column(
        SAEnum(UserStatusEnum, name="user_status_enum"), default=UserStatusEnum.ACTIVE, nullable=False
    )

    # relationships
    tenant = relationship("Tenant", back_populates="users")
    role = relationship("Role", back_populates="users")
    agent = relationship("Agent", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"