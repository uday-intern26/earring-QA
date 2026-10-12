"""Local file helpers. Every served path must stay inside the data directory."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.core.config import get_settings

_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")


class StorageError(Exception):
    def __init__(self, message: str, code: str = "STORAGE_ERROR") -> None:
        super().__init__(message)
        self.code = code


def data_root() -> Path:
    return get_settings().data_dir.resolve()


def ensure_within_data(path: Path) -> Path:
    root = data_root()
    resolved = path.resolve()
    if resolved != root and root not in resolved.parents:
        raise StorageError("Path escapes the data directory.", "INVALID_PATH")
    return resolved


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(name).name).strip("._")
    return cleaned or "upload.bin"


def is_public_id(value: str) -> bool:
    return bool(_ID_RE.match(value))
