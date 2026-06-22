"""
WhatsApp Cloud API webhook integration.

This module defines a FastAPI router that implements the WhatsApp
Business Cloud webhook verification and inbound message handling.

Reference: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples/

The GET handler verifies the webhook challenge using the ``whatsapp_verify_token``
configured in settings.  The POST handler receives inbound messages,
extracts the relevant fields and persists them via the messaging service.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request

from ..core.config import settings
from ..core.database import get_session
from ..schemas.message import MessageInbound
from ..services.messaging_service import handle_inbound_message
from ..services.job_service import create_job
import uuid
from ..schemas.job import JobCreate
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])
logger = logging.getLogger(__name__)


@router.get("/")
async def verify_webhook(mode: str | None = None, token: str | None = None, challenge: str | None = None):
    """Verify webhook endpoint.

    Facebook/WhatsApp will send a GET request with ``hub.mode``, ``hub.verify_token``
    and ``hub.challenge`` parameters.  If the verify_token matches the configured
    token, echo back the challenge; otherwise return 403.
    """
    # Parameter names are typically hub.mode, hub.verify_token, hub.challenge
    # FastAPI automatically captures query params; alias names can be used but
    # this simple implementation uses names directly.
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        return int(challenge) if challenge is not None else 200
    raise HTTPException(status_code=403, detail="Invalid verify token")


@router.post("/")
async def receive_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Handle incoming messages from WhatsApp.

    The payload structure may contain various event types.  This handler
    iterates through the entries and messaging events, extracts the
    message content, and persists it as an inbound message.  If the
    message appears to be a new request (no job_id), a new job is
    created automatically.
    """
    body = await request.json()
    logger.debug("Received WhatsApp webhook: %s", json.dumps(body))
    # Basic parsing: iterate through entry -> changes -> value -> messages
    # Real implementation should handle message types, statuses, etc.
    entries = body.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            for msg in messages:
                # Extract required fields
                from_id = msg.get("from")
                text_body = msg.get("text", {}).get("body")
                if not text_body:
                    continue
                # Derive tenant_id from metadata: you may store phone numbers mapping to tenant
                # For demonstration, assume a single tenant id from settings or environment
                # In production, map the phone number to tenant.
                # Here we raise if tenant_id missing in query params or environment.
                try:
                    tenant_id = uuid.UUID(value.get("metadata", {}).get("tenant_id"))  # type: ignore
                except Exception:
                    # Fallback to default tenant id in settings if configured
                    logger.warning("No tenant_id in metadata; dropping message")
                    continue
                inbound = MessageInbound(
                    tenant_id=tenant_id,
                    job_id=None,
                    customer_contact=from_id,
                    channel="whatsapp",
                    content=text_body,
                    extra_metadata={},
                )
                # Persist inbound message
                msg_obj = await handle_inbound_message(session, inbound)
                # Simple heuristic: if there is no job_id, create a new job
                # with the content as title.  Use classification tasks in production.
                if not msg_obj.job_id:
                    job_in = JobCreate(
                        tenant_id=inbound.tenant_id,
                        customer_id=None,
                        title=text_body[:50],
                        description=text_body,
                        type="general",
                        priority="medium",
                    )
                    job = await create_job(session, job_in)  # create new job
                    # Associate message with job
                    msg_obj.job_id = job.id
                    session.add(msg_obj)
                    await session.commit()
    return {"status": "received"}