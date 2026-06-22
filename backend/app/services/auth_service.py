"""
Service for authentication and JWT token management.

This service handles hashing and verifying passwords, creating access
and refresh JWTs, and decoding tokens.  It uses ``passlib`` for
password hashing and ``python-jose`` for JWT encoding/decoding.
"""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Optional, Any, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | uuid.UUID,
    expires_delta: Optional[dt.timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT access token.

    Parameters
    ----------
    subject: str | uuid.UUID
        The subject claim, typically the user's ID.
    expires_delta: Optional[timedelta]
        How long the token is valid for; defaults to settings.access_token_expire_minutes.
    additional_claims: dict
        Optional additional claims to include in the token.

    Returns
    -------
    str
        Encoded JWT token.
    """
    if expires_delta is None:
        expires_delta = dt.timedelta(minutes=settings.access_token_expire_minutes)
    expire = dt.datetime.utcnow() + expires_delta
    to_encode: Dict[str, Any] = {"sub": str(subject), "exp": expire}
    if additional_claims:
        to_encode.update(additional_claims)
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(
    subject: str | uuid.UUID,
    expires_delta: Optional[dt.timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed JWT refresh token."""
    if expires_delta is None:
        expires_delta = dt.timedelta(minutes=settings.refresh_token_expire_minutes)
    expire = dt.datetime.utcnow() + expires_delta
    to_encode: Dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "refresh"}
    if additional_claims:
        to_encode.update(additional_claims)
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token and return the payload.

    Raises
    ------
    JWTError
        If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as exc:
        raise exc