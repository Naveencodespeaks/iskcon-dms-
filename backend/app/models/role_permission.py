"""
Association table linking roles and permissions.

Many‑to‑many relationships between Role and Permission are modelled via
this table.  Additional fields (e.g., assignment date) can be added
later if needed.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from .base import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    permission_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint("role_id", "permission_id", name="pk_role_permissions"),
    )