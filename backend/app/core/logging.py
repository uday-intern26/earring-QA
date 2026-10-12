"""Structured JSON logs. Event names match the QA pipeline stages."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from app.core.security import RedactFilter, redact_mapping, secret_registry

_CONFIGURED = False


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = secret_registry.redact(record.getMessage())
        event = getattr(record, "event_name", None) or message
        payload: dict = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "event": event,
            "message": message,
            "logger": record.name,
        }
        extra = getattr(record, "extra_data", None)
        if isinstance(extra, dict):
            payload.update(redact_mapping(extra))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RedactFilter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
    _CONFIGURED = True


def log_event(event: str, level: int = logging.INFO, **fields: object) -> None:
    logger = logging.getLogger("aijewel.qa")
    logger.log(level, event, extra={"event_name": event, "extra_data": fields})
