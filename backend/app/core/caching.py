"""
Redis caching and messaging client.

This module initializes a single Redis client instance using
``redis.asyncio`` (available in redis-py >= 4.2).  Use this client
across the application for caching tokens, storing session data or
publishing events to streams.  Connection errors should be handled
where the client is used.
"""

from __future__ import annotations

import redis.asyncio as aioredis

from .config import settings

redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)