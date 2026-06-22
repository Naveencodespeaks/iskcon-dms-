"""
Celery tasks for document ingestion.

Defines a task that will ingest a document by its ID.  It loads the
document from the database, reads the file contents, computes
embeddings via the RAG service and stores them in Qdrant.  This task
should be invoked asynchronously after a document is uploaded.
"""

from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.celery_app import celery_app
from ..core.database import AsyncSessionLocal
from ..models.document import Document
from ..services.rag_service import ingest_document


@celery_app.task
def ingest_document_task(document_id: str):
    """Celery task to ingest a document by ID."""
    async def _run():
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            doc = await session.get(Document, document_id)
            if not doc:
                return
            await ingest_document(session, doc, str(doc.tenant_id))
    asyncio.get_event_loop().run_until_complete(_run())