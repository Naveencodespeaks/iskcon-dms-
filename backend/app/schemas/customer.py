"""
Pydantic schemas for customers and contacts.
"""

from __future__ import annotations

import uuid
from typing import Optional, List

from pydantic import BaseModel, Field


class ContactRead(BaseModel):
    id: uuid.UUID
    channel: str
    handle: str
    is_primary: bool

    class Config:
        orm_mode = True


class CustomerBase(BaseModel):
    name: str = Field(..., description="Customer name")
    contact_info: Optional[dict] = Field(None, description="Contact information as JSON")
    extra_metadata: Optional[dict] = Field(None, description="Additional metadata about the customer")


class CustomerCreate(CustomerBase):
    tenant_id: uuid.UUID


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[dict] = None
    extra_metadata: Optional[dict] = None


class CustomerRead(CustomerBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    contacts: List[ContactRead] = []

    class Config:
        orm_mode = True