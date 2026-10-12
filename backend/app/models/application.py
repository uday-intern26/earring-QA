from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Application(SQLModel, table=True):
    __tablename__ = "applications"

    id: str = Field(primary_key=True)
    name: str
    type: str = Field(index=True, description="web, desktop, or video")
    url: str | None = None
    executable_path: str | None = None
    video_path: str | None = None
    anchor_file: str | None = None
    username: str | None = None
    username_selector: str | None = None
    password_selector: str | None = None
    submit_selector: str | None = None
    ready_selector: str | None = None
    last_validation_status: str | None = None
    last_validation_message: str | None = None
    validation_screenshot: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
