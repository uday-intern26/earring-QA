"""Persists the QA report JSON consumed by the dashboard."""

from __future__ import annotations

from pathlib import Path

from app.utils.files import write_json


class ReportService:
    def write(self, directory: Path, report: dict) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / "report.json"
        write_json(path, report)
        write_json(directory / "result.json", report)
        return path
