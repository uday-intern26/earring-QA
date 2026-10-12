import math

import pytest

from app.utils.geometry import (
    angle_error,
    direction_degrees,
    distance,
    ellipse_radii,
    normalize_distance,
    offset,
    point_in_ellipse,
    vector_error,
)
from app.utils.validators import classify_placement


def test_distance_and_normalization_match_the_spec_formula():
    dx, dy = offset(0.424, 0.375, 0.421, 0.372)
    assert dx == pytest.approx(0.003)
    assert dy == pytest.approx(0.003)
    raw = distance(dx, dy)
    assert raw == pytest.approx(math.hypot(0.003, 0.003))
    assert normalize_distance(dx, dy, ear_width=0.06) == pytest.approx(raw / 0.06)


def test_zone_scale_changes_only_the_vertical_axis():
    circular = normalize_distance(0.0, 0.02, ear_width=0.1, zone_y_scale=1)
    taller = normalize_distance(0.0, 0.02, ear_width=0.1, zone_y_scale=2)
    assert circular == pytest.approx(0.2)
    assert taller == pytest.approx(0.1)


def test_angle_error_wraps_across_zero():
    assert angle_error(10, 350) == pytest.approx(20)
    assert direction_degrees(1, 0) == pytest.approx(0)
    assert vector_error(0.1, 0.2, 0.1, 0.2) == pytest.approx(0)


def test_point_in_ellipse_uses_normalized_distance():
    assert point_in_ellipse(0.003, 0.003, ear_width=0.06, max_normalized_distance=0.15)
    assert not point_in_ellipse(0.02, 0.02, ear_width=0.06, max_normalized_distance=0.15)
    radius_x, radius_y = ellipse_radii(0.06, 0.15, 1)
    assert radius_x == pytest.approx(0.009)
    assert radius_y == pytest.approx(0.009)


@pytest.mark.parametrize(
    ("distance_value", "confidence", "expected"),
    [
        (0.10, 0.90, "PASS"),
        (0.12, 0.90, "WARNING"),
        (0.15, 0.90, "WARNING"),
        (0.16, 0.90, "FAIL"),
        (0.01, 0.50, "FAIL"),
    ],
)
def test_pass_warning_fail_thresholds(distance_value, confidence, expected):
    status, _reason = classify_placement(
        distance_value,
        confidence,
        minimum_confidence=0.80,
        pass_threshold=0.10,
        fail_threshold=0.15,
        dy=0.01,
        dx=0.0,
    )
    assert status == expected


def test_missing_anchors_fail():
    status, reason = classify_placement(
        0,
        0,
        minimum_confidence=0.8,
        pass_threshold=0.1,
        fail_threshold=0.15,
        missing_earlobe=True,
    )
    assert status == "FAIL"
    assert "Earlobe" in reason


def test_earring_below_lobe_is_called_out():
    status, reason = classify_placement(
        0.31,
        0.99,
        minimum_confidence=0.8,
        pass_threshold=0.10,
        fail_threshold=0.15,
        dx=0.003,
        dy=0.14,
    )
    assert status == "FAIL"
    assert "below" in reason
