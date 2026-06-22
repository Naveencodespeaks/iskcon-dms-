"""
Logging configuration for the backend application.

Uses Python's built‑in logging module to output structured logs in
JSON format.  For production deployments, integrate with logging
aggregators (e.g., ELK, Loki) and attach correlation IDs via
middleware.
"""

import logging
import sys
import json
from typing import Any, Dict


class JsonFormatter(logging.Formatter):
    """Formatter that outputs logs as JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
            "name": record.name,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logger to output JSON logs to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]