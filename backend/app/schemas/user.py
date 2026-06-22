"""
Pydantic schemas for User models.

These schemas define the shape of user data exchanged via the API.  Use
``UserCreate`` when creating a new user, ``UserRead`` when reading
user data from the database and returning it to clients, and
``UserUpdate`` for partial updates.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    name: str = Field(..., description="Full name of the user")
    role_id: Optional[uuid.UUID] = Field(None, description="Role identifier")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Plaintext password for the user")
    tenant_id: uuid.UUID = Field(..., description="Tenant identifier to which the user belongs")


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role_id: Optional[uuid.UUID] = None
    status: Optional[str] = Field(None, description="User status (active/inactive)")


class UserRead(UserBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    status: str

    class Config:
        orm_mode = True