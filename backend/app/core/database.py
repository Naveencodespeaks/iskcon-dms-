"""
Database module providing SQLAlchemy async engine and session management.

This module configures the database engine using the connection string
defined in the application settings.  It exposes a generator
``get_session`` that can be used as a dependency in FastAPI routes to
provide an `AsyncSession` scoped to the request context.

The application uses the SQLAlchemy 2.0 style async engine with
``asyncpg`` as the underlying driver for PostgreSQL.  Sessions are
configured not to expire on commit so that objects remain accessible
after writes.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings


# Create the async engine.  The pool_pre_ping option helps the engine
# detect stale connections and recover gracefully.
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    future=True,
)

# Session maker factory.  expire_on_commit=False prevents SQLAlchemy from
# expiring objects after commit; this makes objects available after
# transaction commit within the same session.
AsyncSessionLocal = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a new database session.

    Yields
    ------
    AsyncSession
        An SQLAlchemy async session bound to the configured engine.

    When the request finishes the session is closed automatically by the
    context manager.  Exceptions inside the request will roll back the
    transaction.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            # Session is closed by context manager when exiting
            pass