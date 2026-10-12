from datetime import datetime

from pydantic import BaseModel, Field


class ReferenceRead(BaseModel):
    id: str
    filename: str
    path: str
    width: int
    height: int
    side: str | None
    earlobe_x: float | None
    earlobe_y: float | None
    earring_x: float | None
    earring_y: float | None
    ear_width: float | None
    ear_height: float | None
    vector_dx: float | None
    vector_dy: float | None
    normalized_distance: float | None
    confidence: float | None
    analysis_error: str | None
    image_url: str
    created_at: datetime


class ReferenceAnchorUpdate(BaseModel):
    side: str = Field(pattern="^(left|right)$")
    earlobe_x: float = Field(ge=0, le=1)
    earlobe_y: float = Field(ge=0, le=1)
    earring_x: float = Field(ge=0, le=1)
    earring_y: float = Field(ge=0, le=1)
    ear_width: float = Field(gt=0, le=1)
    ear_height: float = Field(gt=0, le=1, default=0.08)
