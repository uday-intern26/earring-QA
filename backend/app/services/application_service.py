"""Application records. Passwords are never written to the database."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlmodel import Session, select

from app.db.database import allocate_id
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate


class ApplicationService:
    def create(self, session: Session, payload: ApplicationCreate) -> Application:
        self._validate_target(payload)
        record = Application(
            id=allocate_id(session, "APP", Application),
            name=payload.name.strip(),
            type=payload.type,
            url=payload.url,
            executable_path=payload.executable_path,
            video_path=payload.video_path,
            anchor_file=payload.anchor_file,
            username=payload.username,
            username_selector=payload.username_selector,
            password_selector=payload.password_selector,
            submit_selector=payload.submit_selector,
            ready_selector=payload.ready_selector,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    def list(self, session: Session) -> list[Application]:
        return list(session.exec(select(Application).order_by(Application.created_at.desc())).all())

    def get(self, session: Session, application_id: str) -> Application | None:
        return session.get(Application, application_id)

    def update_target(self, session: Session, application: Application, payload: ApplicationUpdate) -> Application:
        if application.type == "web" and payload.url is not None and not payload.url.strip():
            raise ValueError("A web application requires a URL.")
        if payload.url is not None:
            application.url = payload.url.strip()
        if payload.username is not None:
            application.username = payload.username.strip() or None
        application.updated_at = datetime.now(timezone.utc)
        session.add(application)
        session.commit()
        session.refresh(application)
        return application

    def attach_face_video(
        self,
        session: Session,
        application: Application,
        *,
        filename: str,
        content: bytes,
        captures_dir: Path,
    ) -> Application:
        if application.type != "web":
            raise ValueError("Upload the bare-ear face video on the try-on URL application.")
        suffix = Path(filename).suffix.lower()
        if suffix not in {".mp4", ".webm", ".mov"}:
            raise ValueError("Upload an mp4, webm, or mov of a person wearing no earrings.")
        if not content:
            raise ValueError("The face video file is empty.")
        captures_dir.mkdir(parents=True, exist_ok=True)
        for existing in captures_dir.iterdir():
            if existing.is_file() and existing.suffix.lower() in {".mp4", ".webm", ".mov", ".y4m", ".avi"}:
                existing.unlink()
        destination = captures_dir / "bare-face.mp4"
        destination.write_bytes(content)
        application.video_path = str(destination)
        application.updated_at = datetime.now(timezone.utc)
        session.add(application)
        session.commit()
        session.refresh(application)
        return application

    def mark_validation(
        self,
        session: Session,
        application: Application,
        *,
        status: str,
        message: str,
        screenshot: str | None,
    ) -> Application:
        application.last_validation_status = status
        application.last_validation_message = message
        application.validation_screenshot = screenshot
        application.updated_at = datetime.now(timezone.utc)
        session.add(application)
        session.commit()
        session.refresh(application)
        return application

    def _validate_target(self, payload: ApplicationCreate) -> None:
        if payload.type == "web" and not payload.url:
            raise ValueError("A web application requires a URL.")
        if payload.type == "video" and not payload.video_path:
            raise ValueError("A video/file application requires a video path.")
        if payload.type == "desktop" and not payload.executable_path:
            raise ValueError("A desktop application requires an executable path.")
