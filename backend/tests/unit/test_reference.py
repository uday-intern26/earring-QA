import pytest

from app.cv.anchor_geometry import compare_reference, reference_vector_from_points
from app.cv.types import PlacementMeasurement


def _vector(earring_x: float, earring_y: float):
    return reference_vector_from_points(
        earlobe_x=0.40,
        earlobe_y=0.50,
        earring_x=earring_x,
        earring_y=earring_y,
        ear_width=0.08,
        ear_height=0.16,
    )


def test_reference_vector_is_relative_not_pixel_based():
    vector = _vector(0.41, 0.51)
    assert vector.dx == pytest.approx(0.01)
    assert vector.dy == pytest.approx(0.01)
    assert vector.normalized_distance == pytest.approx(vector.magnitude / 0.08)


def test_matching_vectors_pass():
    reference = _vector(0.405, 0.504)
    actual = PlacementMeasurement(
        dx=reference.dx,
        dy=reference.dy,
        normalized_distance=reference.normalized_distance,
        status="PASS",
        reason="",
    )
    comparison = compare_reference(reference, actual, pass_threshold=0.10, fail_threshold=0.15)
    assert comparison.status == "PASS"
    assert comparison.distance_error == 0
    assert comparison.angle_error == 0


def test_large_distance_and_angle_fail():
    reference = _vector(0.41, 0.50)
    actual = PlacementMeasurement(
        dx=-0.04,
        dy=0.05,
        normalized_distance=0.4,
        status="FAIL",
        reason="",
    )
    comparison = compare_reference(reference, actual, pass_threshold=0.10, fail_threshold=0.15)
    assert comparison.status == "FAIL"
    assert comparison.distance_error > 0.15
    assert comparison.angle_error > 35
