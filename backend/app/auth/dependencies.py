"""
Dependency helpers for authentication and current user retrieval.

This module defines reusable FastAPI dependencies that decode JWT tokens,
load the corresponding user from the database, and optionally verify
that the user is active.  It relies on the ``auth_service`` for JWT
operations and is intended to be imported by route modules.

Example usage::

    from fastapi import Depends, APIRouter
    from ..auth.dependencies import get_current_active_user

    router = APIRouter()

    @router.get("/me")
    async def read_current_user(current_user=Depends(get_current_active_user)):
        return current_user

"""

from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..core.database import get_session
from ..models.user import User, UserStatusEnum
from ..models.role import Role
from ..services.auth_service import decode_token


# OAuth2 scheme for receiving the Bearer token in Authorization header.
# The tokenUrl is set to the login endpoint relative to the API base.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Retrieve the currently authenticated user from the JWT token.

    Parameters
    ----------
    token: str
        JWT access token supplied via OAuth2 bearer auth.
    session: AsyncSession
        Database session dependency.

    Returns
    -------
    User
        The user object corresponding to the subject of the token.

    Raises
    ------
    HTTPException
        If the token is invalid, expired or the user does not exist.
    """
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing subject in token")
    user_id: uuid.UUID
    try:
        user_id = uuid.UUID(str(subject))
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid subject in token")
    # Query the user by ID with role + permissions eagerly loaded for RBAC
    stmt = select(User).where(User.id == user_id).options(
        selectinload(User.role).selectinload(Role.permissions)
    )
    result = await session.execute(stmt)
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Ensure the current user is active.

    Raises HTTPException if the user is inactive or pending.
    """
    if current_user.status != UserStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive or pending user",
        )
    return current_user


async def get_current_tenant_id(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> uuid.UUID:
    """Return the tenant_id of the current user.

    Many endpoints require the tenant_id to scope queries.  Use this
    dependency to extract the tenant identifier from the authenticated
    user record.
    """
    return current_user.tenant_id