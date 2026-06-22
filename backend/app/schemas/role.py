"""
Pydantic schemas for Role and Permission models.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from pydantic import BaseModel, Field


class PermissionRead(BaseModel):
    id: uuid.UUID
    code: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class RoleBase(BaseModel):
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    permissions: Optional[List[uuid.UUID]] = Field(
        None, description="List of permission identifiers to attach to this role"
    )


class RoleCreate(RoleBase):
    tenant_id: uuid.UUID


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[uuid.UUID]] = None


class RoleRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: Optional[str] = None
    permissions: List[PermissionRead] = []

    class Config:
        orm_mode = True