"""
Alembic environment configuration for asynchronous migrations.

This file configures Alembic to work with SQLAlchemy's async engine
defined in ``app.core.database`` and to autogenerate migrations from
models defined in ``app.models``.  To create a new migration, run

    alembic revision --autogenerate -m "message"

and to apply migrations, run

    alembic upgrade head

Note: Alembic's async support requires SQLAlchemy 1.4+ and does not
support autogenerate for async models directly; however, because the
models themselves are synchronous declarations, autogeneration works.
"""

from __future__ import annotations

import asyncio
import logging
from logging.config import fileConfig
from typing import Optional

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

import sys
import os

# Ensure we can import the app package when alembic loads this file directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.core.config import settings
from app.core.database import engine as target_engine
from app.models import *  # noqa: F401,F403 import models for metadata
from app.models.base import Base

config = context.config

# Logging config is optional in minimal alembic.ini
if config.config_file_name and config.get_section('loggers'):
    try:
        fileConfig(config.config_file_name)
    except Exception:
        pass

logger = logging.getLogger('alembic.env')

# add your model's MetaData object here
target_metadata = Base.metadata  # type: ignore[name-defined]


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.database_url.replace('+asyncpg', '')  # Use sync dialect for offline
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using the async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
        future=True,
        url=settings.database_url,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())