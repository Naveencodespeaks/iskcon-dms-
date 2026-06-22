"""
Pydantic schemas for permissions.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    code: str = Field(..., description="Unique code of the permission")
    description: Optional[str] = Field(None, description="Human readable description")


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase):
    id: uuid.UUID

    class Config:
        orm_mode = True