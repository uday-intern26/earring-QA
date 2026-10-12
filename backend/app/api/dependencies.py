"""FastAPI dependencies."""

from collections.abc import Iterator

from sqlmodel import Session

from app.core.config import Settings, get_settings
from app.db.database import get_session as _get_session


def get_db() -> Iterator[Session]:
    yield from _get_session()


def get_app_settings() -> Settings:
    return get_settings()
