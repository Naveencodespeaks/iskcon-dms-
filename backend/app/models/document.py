"""
ORM model for Documents.

Documents store metadata about files uploaded by tenants.  The actual
file contents live in object storage (e.g., S3, MinIO); the file_path
stores a reference to the location.  When ingestion is complete
(``ingested`` set to true), corresponding embeddings are stored in
Qdrant.  Additional metadata (title, author, etc.) can be stored in
the JSON column.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Column, String, JSON, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Document(TimestampMixin, Base):
    __tablename__ = "documents"

    id: uuid.UUID = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    tenant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    file_path: str = Column(String(512), nullable=False)
    file_type: str = Column(String(50), nullable=False)
    extra_metadata: dict | None = Column(JSON, nullable=True)
    ingested: bool = Column(Boolean, default=False, nullable=False)

    tenant = relationship("Tenant", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document id={self.id} path={self.file_path}>"