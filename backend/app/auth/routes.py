"""
Authentication API routes.

This module defines endpoints for user login, registration and token
refresh.  It uses the ``auth_service`` to verify credentials and
issue JWT access and refresh tokens.  These routes are mounted under
``/api/v1/auth`` in the main application.

"""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..models.user import User
from ..schemas.user import UserCreate, UserRead
from ..services.auth_service import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, session: AsyncSession = Depends(get_session)) -> User:
    """Register a new user account.

    This endpoint creates a new user record associated with a tenant.  It
    does not enforce any permission checks; in production, restrict
    registration to administrators or onboarding flows.  The
    plaintext password is hashed before storage.
    """
    # Check if email already exists for tenant
    stmt = select(User).where(User.email == user_in.email, User.tenant_id == user_in.tenant_id)
    existing = (await session.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
    hashed = get_password_hash(user_in.password)
    user = User(
        tenant_id=user_in.tenant_id,
        email=user_in.email,
        name=user_in.name,
        password_hash=hashed,
        role_id=user_in.role_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login")
async def login(form_data: Dict[str, Any], session: AsyncSession = Depends(get_session)) -> Dict[str, Any]:
    """Authenticate a user and return access and refresh tokens.

    Expects a JSON payload with ``email`` and ``password`` fields.  On
    successful authentication, returns a dict containing ``access_token``
    and ``refresh_token``.  If credentials are invalid, raises 401.
    """
    email = form_data.get("email")
    password = form_data.get("password")
    if not email or not password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing email or password")
    stmt = select(User).where(User.email == email)
    user = (await session.execute(stmt)).scalars().first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    additional_claims = {"tenant_id": str(user.tenant_id), "role_id": str(user.role_id) if user.role_id else None}
    access_token = create_access_token(subject=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(subject=str(user.id), additional_claims=additional_claims)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh_token_endpoint(
    form_data: Dict[str, Any],
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """Exchange a refresh token for a new access token.

    The request body must contain a ``refresh_token`` field.  The
    refresh token must have ``type`` set to ``refresh``.  If valid,
    returns a new short‑lived access token.
    """
    refresh_token = form_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing refresh token")
    try:
        payload = decode_token(refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    additional_claims = {"tenant_id": str(user.tenant_id), "role_id": str(user.role_id) if user.role_id else None}
    new_access_token = create_access_token(subject=str(user.id), additional_claims=additional_claims)
    return {"access_token": new_access_token, "token_type": "bearer"}