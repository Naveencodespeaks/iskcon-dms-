"""
Pydantic schemas for documents.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    file_type: str = Field(..., description="Type of the file (pdf, docx, etc.)")
    extra_metadata: Optional[dict] = None


class DocumentCreate(DocumentBase):
    tenant_id: uuid.UUID


class DocumentRead(DocumentBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    file_path: str
    ingested: bool

    class Config:
        orm_mode = True