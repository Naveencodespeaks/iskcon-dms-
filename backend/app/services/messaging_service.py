"""
Messaging service for handling inbound and outbound messages.

Messages can originate from customers via WhatsApp webhooks or from
agents/automations.  This service normalizes inbound messages,
persists them and enqueues further processing.  Outbound messages are
sent via WhatsApp or other channels; for now this service provides a
placeholder implementation.
"""

from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.message import Message
from ..schemas.message import MessageInbound, MessageOutbound


async def handle_inbound_message(session: AsyncSession, inbound: MessageInbound) -> Message:
    """Persist an inbound message into the database.

    Parameters
    ----------
    session: AsyncSession
        Database session.
    inbound: MessageInbound
        Data transfer object containing inbound message data.

    Returns
    -------
    Message
        Persisted message instance.
    """
    msg = Message(
        tenant_id=inbound.tenant_id,
        job_id=inbound.job_id,
        sender_id=None,  # inbound messages have no internal sender
        channel=inbound.channel,
        content=inbound.content,
        extra_metadata=inbound.extra_metadata or {},
        timestamp=dt.datetime.utcnow(),
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    # TODO: Publish event to classification/assignment engine
    return msg


async def send_outbound_message(session: AsyncSession, outbound: MessageOutbound) -> Message:
    """Send a message to a customer and record it.

    This implementation persists the message in the database and
    simulates sending via WhatsApp by logging.  In production, this
    function would call the WhatsApp Cloud API using the credentials
    configured for the tenant.
    """
    msg = Message(
        tenant_id=None,  # Outbound messages derive tenant from job relationship
        job_id=outbound.job_id,
        sender_id=None,
        channel=outbound.channel,
        content=outbound.content,
        extra_metadata=outbound.extra_metadata or {},
        timestamp=dt.datetime.utcnow(),
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    # Simulate sending by printing to stdout; replace with HTTP call to WhatsApp
    print(f"Sending outbound {outbound.channel} message: {outbound.content}")
    return msg