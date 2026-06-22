"""
Document management endpoints.

This router provides CRUD operations for documents and an endpoint to
trigger ingestion into the vector database.  In a production system,
file uploads would be handled via multipart/form‑data, stored in
object storage and then processed asynchronously.  For simplicity,
this API accepts a ``file_path`` string referencing a file already
available on disk.
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...models.document import Document
from ...schemas.document import DocumentCreate, DocumentRead
from ...auth.dependencies import get_current_tenant_id
from ...rbac.dependencies import permission_required
from ...services.ingestion_service import create_document, trigger_ingestion


router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.get("/", response_model=List[DocumentRead])
async def list_documents(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("documents:view"),
) -> List[Document]:
    """List all documents for the current tenant."""
    result = await session.execute(select(Document).where(Document.tenant_id == tenant_id))
    return result.scalars().all()


@router.post("/", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    doc_in: DocumentCreate,
    file_path: str,
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("documents:create"),
) -> Document:
    """Create a Document record and trigger ingestion.

    ``file_path`` should point to a file on disk accessible by the backend.
    After the record is created, ingestion is triggered asynchronously.
    """
    document = await create_document(session, doc_in, file_path=file_path)
    # Trigger ingestion asynchronously (not awaited)
    await trigger_ingestion(session, document)
    return document


@router.get("/{doc_id}", response_model=DocumentRead)
async def get_document(
    doc_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("documents:view"),
) -> Document:
    """Retrieve a single document by ID."""
    doc = await session.get(Document, doc_id)
    if not doc or doc.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


@router.post("/{doc_id}/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_document_endpoint(
    doc_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("documents:ingest"),
) -> dict:
    """Trigger ingestion of a document into the vector store.

    This endpoint simply enqueues the ingestion task; it does not wait
    for completion.  Returns a 202 Accepted status.
    """
    doc = await session.get(Document, doc_id)
    if not doc or doc.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    # Trigger ingestion asynchronously (not awaited)
    await trigger_ingestion(session, doc)
    return {"detail": "Ingestion started"}