"""
Celery application factory.

Defines the Celery app used for background tasks such as document
ingestion, embedding generation, classification and assignment
calculations.  Configure the broker and result backend using
environment variables loaded from settings.
"""

from __future__ import annotations

from celery import Celery

from .config import settings


def create_celery() -> Celery:
    """Create and return a configured Celery application."""
    celery_app = Celery(
        "copilot_tasks",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
    )
    celery_app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_track_started=True,
        broker_transport_options={"visibility_timeout": 3600},
    )
    return celery_app


celery_app = create_celery()