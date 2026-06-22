"""
Tenant management endpoints.

This router exposes endpoints to create and list tenants.  Creating a
tenant may also involve onboarding workflows such as uploading
documents and setting up roles; for simplicity this API only
persists the tenant record.  Listing tenants is restricted to
administrators.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...models.tenant import Tenant
from ...schemas.tenant import TenantCreate, TenantRead
from ...auth.dependencies import get_current_active_user
from ...rbac.dependencies import permission_required


router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


@router.get("/", response_model=List[TenantRead])
async def list_tenants(
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("tenants:view"),
) -> List[Tenant]:
    """List all tenants.  Only available to users with ``tenants:view`` permission."""
    result = await session.execute(select(Tenant))
    return result.scalars().all()


@router.post("/", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_in: TenantCreate,
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("tenants:create"),
) -> Tenant:
    """Create a new tenant.

    Users with the ``tenants:create`` permission can onboard a new tenant.
    """
    # Check for uniqueness
    existing = (await session.execute(select(Tenant).where(Tenant.name == tenant_in.name))).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant name already exists")
    tenant = Tenant(name=tenant_in.name, industry=tenant_in.industry, settings=tenant_in.settings)
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)
    return tenant