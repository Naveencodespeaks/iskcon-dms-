"""
Qdrant vector database wrapper.

Provides helper functions to initialize a client and manage
collections.  Use this module when interacting with Qdrant outside of
the RAG service, such as when purging collections or obtaining
statistics.
"""

from __future__ import annotations

from qdrant_client import QdrantClient

from .config import settings


def get_client() -> QdrantClient:
    """Return a Qdrant client configured from settings."""
    return QdrantClient(url=settings.qdrant_url)