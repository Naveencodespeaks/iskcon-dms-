"""
Role management endpoints.

This router provides CRUD APIs for roles and permissions.  Roles group
permissions and are assigned to users.  Only users with the
appropriate permissions may create or modify roles.
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...models.role import Role
from ...models.permission import Permission
from ...schemas.role import RoleCreate, RoleRead, RoleUpdate
from ...auth.dependencies import get_current_tenant_id
from ...rbac.dependencies import permission_required

router = APIRouter(prefix="/api/v1/roles", tags=["roles"])


@router.get("/", response_model=List[RoleRead])
async def list_roles(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("roles:view"),
) -> List[Role]:
    """List all roles for the current tenant."""
    result = await session.execute(select(Role).where(Role.tenant_id == tenant_id))
    return result.scalars().all()


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_in: RoleCreate,
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("roles:create"),
) -> Role:
    """Create a role and attach permissions."""
    # Validate permission IDs
    permissions = []
    if role_in.permissions:
        for pid in role_in.permissions:
            perm = await session.get(Permission, pid)
            if not perm:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Permission {pid} not found")
            permissions.append(perm)
    role = Role(tenant_id=role_in.tenant_id, name=role_in.name, description=role_in.description)
    role.permissions = permissions
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: uuid.UUID,
    role_in: RoleUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("roles:update"),
) -> Role:
    """Update a role's name/description and permissions."""
    role = await session.get(Role, role_id)
    if not role or role.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role_in.name is not None:
        role.name = role_in.name
    if role_in.description is not None:
        role.description = role_in.description
    if role_in.permissions is not None:
        permissions: List[Permission] = []
        for pid in role_in.permissions:
            perm = await session.get(Permission, pid)
            if not perm:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Permission {pid} not found")
            permissions.append(perm)
        role.permissions = permissions
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role