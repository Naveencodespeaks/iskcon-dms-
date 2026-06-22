"""
Pydantic schemas for Tenant models.

Tenants represent organizations.  ``TenantCreate`` is used when
onboarding new tenants; ``TenantRead`` returns tenant details to the
client.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field


class TenantBase(BaseModel):
    name: str = Field(..., description="Name of the tenant organisation")
    industry: Optional[str] = Field(None, description="Industry vertical")
    settings: Optional[dict] = Field(None, description="Tenant configuration settings")


class TenantCreate(TenantBase):
    pass


class TenantRead(TenantBase):
    id: uuid.UUID
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        orm_mode = True