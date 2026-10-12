"""Computer-vision domain types. Coordinates are normalized from 0 to 1."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Landmark(BaseModel):
    x: float
    y: float
    z: float = 0.0
    confidence: float = 1.0


class HeadPose(BaseModel):
    yaw: float
    pitch: float
    roll: float


class FaceLandmarkResult(BaseModel):
    face_detected: bool
    landmarks: list[Landmark] = Field(default_factory=list)
    confidence: float = 0.0
    head_pose: HeadPose | None = None
    reason: str | None = None


class EarlobeAnchor(BaseModel):
    side: str
    x: float
    y: float
    confidence: float
    ear_width: float
    ear_height: float


class EarringAnchor(BaseModel):
    side: str
    x: float | None = None
    y: float | None = None
    confidence: float = 0.0
    visible: bool = False
    source: str = "missing"
    rotation: float | None = None
    scale: float | None = None
    jewelry_id: str | None = None
    reason: str | None = None


class FrameQuality(BaseModel):
    face_detected: bool
    left_ear_visible: bool
    right_ear_visible: bool
    blur_score: float
    landmark_confidence: float
    head_pose_stable: bool
    occluded: bool = False
    rejection_reasons: list[str] = Field(default_factory=list)


class PlacementMeasurement(BaseModel):
    dx: float | None = None
    dy: float | None = None
    distance: float | None = None
    normalized_distance: float | None = None
    status: str
    reason: str
    earlobe_confidence: float = 0.0
    earring_confidence: float = 0.0
    inside_zone: bool = False


class ReferenceVector(BaseModel):
    dx: float
    dy: float
    magnitude: float
    angle_degrees: float
    normalized_distance: float
    ear_width: float
    ear_height: float
    earlobe_x: float
    earlobe_y: float
    earring_x: float
    earring_y: float


class ReferenceComparison(BaseModel):
    status: str
    magnitude_reference: float | None = None
    magnitude_actual: float | None = None
    distance_error: float | None = None
    angle_error: float | None = None
    vector_error: float | None = None
    reason: str
