from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.application import utcnow


class ReferenceImage(SQLModel, table=True):
    __tablename__ = "references"

    id: str = Field(primary_key=True)
    filename: str
    path: str
    width: int
    height: int
    side: str | None = None
    earlobe_x: float | None = None
    earlobe_y: float | None = None
    earring_x: float | None = None
    earring_y: float | None = None
    ear_width: float | None = None
    ear_height: float | None = None
    vector_dx: float | None = None
    vector_dy: float | None = None
    normalized_distance: float | None = None
    confidence: float | None = None
    analysis_error: str | None = None
    analysis_json: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
