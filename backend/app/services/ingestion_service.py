"""
Document ingestion service.

This module handles creation of Document records and triggers
asynchronous ingestion tasks to build embeddings.  The actual
embedding and indexing logic resides in ``rag_service``.  In
production, ingestion is executed via Celery workers; here we call
``ingest_document`` directly for simplicity.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.document import Document
from ..schemas.document import DocumentCreate
from .rag_service import ingest_document


async def create_document(session: AsyncSession, doc_in: DocumentCreate, file_path: str) -> Document:
    """Persist a new Document record in the database."""
    document = Document(
        tenant_id=doc_in.tenant_id,
        file_path=file_path,
        file_type=doc_in.file_type,
        extra_metadata=getattr(doc_in, 'extra_metadata', None) or getattr(doc_in, 'metadata', None) or {},
        ingested=False,
    )
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


async def trigger_ingestion(session: AsyncSession, document: Document) -> None:
    """Trigger ingestion of the document into the vector database.

    For demonstration, this calls ingest_document directly.  In
    production, you should submit a Celery task and return control to
    the API call immediately.
    """
    await ingest_document(session, document, str(document.tenant_id))