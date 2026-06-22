"""
Message endpoints.

This router exposes endpoints for retrieving messages associated with a
job and sending outbound messages.  Inbound messages from WhatsApp
are handled by the webhook integration and stored via the
``messaging_service``.
"""

from __future__ import annotations

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...models.message import Message
from ...schemas.message import MessageOutbound, MessageRead
from ...services.messaging_service import send_outbound_message
from ...auth.dependencies import get_current_active_user, get_current_tenant_id
from ...rbac.dependencies import permission_required


router = APIRouter(prefix="/api/v1/messages", tags=["messages"])


@router.get("/job/{job_id}", response_model=List[MessageRead])
async def list_messages_for_job(
    job_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("messages:view"),
) -> List[Message]:
    """Return all messages for a given job."""
    result = await session.execute(select(Message).where(Message.job_id == job_id, Message.tenant_id == tenant_id))
    return result.scalars().all()


@router.post("/send", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
    outbound: MessageOutbound,
    current_user = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
    _: None = permission_required("messages:create"),
) -> Message:
    """Send an outbound message to a customer and persist it."""
    # Set sender_id and tenant_id implicitly from current user
    outbound_dict = outbound.dict()
    outbound_dict["extra_metadata"] = outbound.extra_metadata or {}
    # Add metadata for sender
    outbound_dict["extra_metadata"]["sender_id"] = str(current_user.id)
    outbound_updated = MessageOutbound(**outbound_dict)
    msg = await send_outbound_message(session, outbound_updated)
    return msg