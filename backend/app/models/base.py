"""
SQLAlchemy base class definition for declarative models.

All ORM models should inherit from ``Base``.  This file defines the
``Base`` using SQLAlchemy's declarative base.  It also includes a
helper mixin ``TimestampMixin`` that adds ``created_at`` and
``updated_at`` timestamp columns to derived models.  The timestamps
are automatically set when rows are inserted or updated.
"""

from __future__ import annotations

import datetime as dt

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""

    @declared_attr.directive
    def created_at(cls):
        return Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @declared_attr.directive
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )