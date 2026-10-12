import pytest

from app.cv.ear_geometry import LEFT_EAR_CONTOUR, EarlobeAnchorEstimator, EarGeometryError
from app.cv.types import Landmark


def _mesh(confidence: float = 1.0) -> list[Landmark]:
    landmarks = [Landmark(x=0.5, y=0.45, confidence=confidence) for _ in range(478)]
    for index, contour_index in enumerate(LEFT_EAR_CONTOUR):
        if index < 15:
            landmarks[contour_index] = Landmark(
                x=0.30 + (index % 5) * 0.015,
                y=0.42 + (index % 3) * 0.04,
                confidence=confidence,
            )
        else:
            landmarks[contour_index] = Landmark(
                x=0.328 + (index - 15) * 0.004,
                y=0.60,
                confidence=confidence,
            )
    return landmarks


def test_valid_landmark_set_estimates_lower_lobe():
    anchor = EarlobeAnchorEstimator().estimate(_mesh(), "left")
    assert anchor.side == "left"
    assert 0.32 < anchor.x < 0.35
    assert anchor.y == pytest.approx(0.60)
    assert anchor.ear_width == pytest.approx(0.06, abs=0.01)
    assert anchor.confidence >= 0.8


def test_missing_landmarks_raise():
    with pytest.raises(EarGeometryError):
        EarlobeAnchorEstimator().estimate([], "left")


def test_low_confidence_landmarks_stay_below_the_gate():
    anchor = EarlobeAnchorEstimator().estimate(_mesh(confidence=0.05), "left")
    assert anchor.confidence < 0.8


def test_collapsed_ear_is_not_visible():
    landmarks = [Landmark(x=0.5, y=0.5) for _ in range(478)]
    with pytest.raises(EarGeometryError):
        EarlobeAnchorEstimator().estimate(landmarks, "left")
