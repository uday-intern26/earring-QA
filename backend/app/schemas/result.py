from typing import Any

from pydantic import BaseModel


class AnchorPoint(BaseModel):
    x: float
    y: float


class FramePlacement(BaseModel):
    frame_number: int
    timestamp_ms: int
    side: str
    earlobe_detected: bool
    earring_detected: bool
    earlobe: AnchorPoint | None = None
    earring: AnchorPoint | None = None
    earlobe_confidence: float | None = None
    earring_confidence: float | None = None
    dx: float | None = None
    dy: float | None = None
    normalized_distance: float | None = None
    status: str
    reason: str
    automated_result: str
    manual_result: str | None = None
    reviewer: str | None = None
    review_reason: str | None = None
    image_url: str
    annotated_image_url: str | None = None
    frame_id: str


class LayerReport(BaseModel):
    status: str
    detail: str


class ResultReport(BaseModel):
    test_run_id: str
    test_id: str
    test_name: str
    overall_status: str
    reason: str | None = None
    recommended_action: str | None = None
    layers: dict[str, Any]
    statistics: dict[str, Any]
    thresholds: dict[str, Any]
    reference_comparison: dict[str, Any] | None = None
    temporal: dict[str, Any] | None = None
    visual_comparison: dict[str, Any] | None = None
    application: dict[str, Any] | None = None
    jewelry_id: str | None = None
    ear_side: str | None = None
    reference_filename: str | None = None
    frames: list[FramePlacement] = []


class DashboardSummary(BaseModel):
    total_tests: int
    passed: int
    failed: int
    warnings: int
    latest_test: dict[str, Any] | None = None
    latest_failure: dict[str, Any] | None = None
    average_pass_rate: float | None = None
