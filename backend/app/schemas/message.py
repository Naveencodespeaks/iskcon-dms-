"""
Pydantic schemas for messages.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    channel: str = Field(..., description="Communication channel (whatsapp)")
    content: str = Field(..., description="Message body")
    extra_metadata: Optional[dict] = Field(None, description="Additional metadata for the message")


class MessageInbound(MessageBase):
    tenant_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    customer_contact: Optional[str] = Field(None, description="Contact handle of the customer")


class MessageOutbound(MessageBase):
    job_id: uuid.UUID
    recipient_contact: Optional[str] = Field(None, description="Contact handle of the recipient (customer)")


class MessageRead(MessageBase):
    id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    sender_id: Optional[uuid.UUID] = None
    timestamp: str

    class Config:
        orm_mode = True