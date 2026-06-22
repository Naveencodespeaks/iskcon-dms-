"""
RBAC service to check if a user has a given permission.

Permissions are assigned to roles; each user belongs to a role.  This
service exposes helper functions to verify permissions and enforce
least‑privilege access patterns.  Use these helpers in API routes to
protect endpoints.
"""

from __future__ import annotations

from typing import Iterable

from fastapi import HTTPException, status

from ..models.user import User


async def has_permission(user: User, permission_code: str) -> bool:
    """Check whether the given user possesses the specified permission.

    Parameters
    ----------
    user: User
        The user object loaded from the database.  Must include role and
        permissions relationships eager loaded.
    permission_code: str
        The permission code to check.

    Returns
    -------
    bool
        True if user has the permission, False otherwise.
    """
    if not user or not user.role:
        return False
    return any(perm.code == permission_code for perm in user.role.permissions)


async def enforce_permission(user: User, permission_code: str) -> None:
    """Raise an HTTPException if the user lacks the specified permission."""
    if not await has_permission(user, permission_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User lacks required permission: {permission_code}",
        )