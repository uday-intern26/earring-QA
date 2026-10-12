"""Credential handling. Passwords stay in memory for one execution and never enter logs or JSON."""

from __future__ import annotations

import logging
import threading

SENSITIVE_KEYS = {
    "password",
    "secret",
    "api_key",
    "authorization",
    "applitools_api_key",
    "applitoools_api_key",
}


class SecretRegistry:
    def __init__(self) -> None:
        self._secrets: set[str] = set()
        self._lock = threading.Lock()

    def add(self, value: str | None) -> None:
        if not value:
            return
        with self._lock:
            self._secrets.add(value)

    def discard(self, value: str | None) -> None:
        if not value:
            return
        with self._lock:
            self._secrets.discard(value)

    def redact(self, text: str) -> str:
        with self._lock:
            secrets = list(self._secrets)
        for secret in secrets:
            if secret and secret in text:
                text = text.replace(secret, "***")
        return text


secret_registry = SecretRegistry()


def redact_mapping(data: dict) -> dict:
    cleaned: dict = {}
    for key, value in data.items():
        if str(key).lower() in SENSITIVE_KEYS:
            cleaned[key] = "***"
        elif isinstance(value, dict):
            cleaned[key] = redact_mapping(value)
        else:
            cleaned[key] = value
    return cleaned


class RedactFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = secret_registry.redact(record.msg)
        if isinstance(record.args, dict):
            record.args = {key: _redact_value(value) for key, value in record.args.items()}
        elif isinstance(record.args, tuple):
            record.args = tuple(_redact_value(value) for value in record.args)
        return True


def _redact_value(value: object) -> object:
    if isinstance(value, str):
        return secret_registry.redact(value)
    return value
