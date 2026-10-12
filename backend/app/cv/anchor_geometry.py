"""Placement measurements and reference-vector comparison."""

from __future__ import annotations

from app.cv.types import EarlobeAnchor, EarringAnchor, PlacementMeasurement, ReferenceComparison, ReferenceVector
from app.utils.geometry import (
    angle_error,
    direction_degrees,
    distance,
    normalize_distance,
    offset,
    vector_error,
)
from app.utils.validators import classify_placement


def measure_placement(
    earlobe: EarlobeAnchor | None,
    earring: EarringAnchor | None,
    *,
    minimum_confidence: float,
    pass_threshold: float,
    fail_threshold: float,
    zone_y_scale: float = 1.0,
) -> PlacementMeasurement:
    if earlobe is None:
        status, reason = classify_placement(
            math_inf(),
            0.0,
            minimum_confidence=minimum_confidence,
            pass_threshold=pass_threshold,
            fail_threshold=fail_threshold,
            missing_earlobe=True,
        )
        return PlacementMeasurement(status=status, reason=reason)
    if earring is None or earring.x is None or earring.y is None or not earring.visible:
        status, reason = classify_placement(
            math_inf(),
            earring.confidence if earring else 0.0,
            minimum_confidence=minimum_confidence,
            pass_threshold=pass_threshold,
            fail_threshold=fail_threshold,
            missing_earring=True,
        )
        return PlacementMeasurement(
            status=status,
            reason=earring.reason or reason if earring else reason,
            earlobe_confidence=earlobe.confidence,
            earring_confidence=earring.confidence if earring else 0.0,
        )

    dx, dy = offset(earring.x, earring.y, earlobe.x, earlobe.y)
    raw = distance(dx, dy)
    normalized = normalize_distance(dx, dy, earlobe.ear_width, zone_y_scale)
    confidence = min(earlobe.confidence, earring.confidence)
    status, reason = classify_placement(
        normalized,
        confidence,
        minimum_confidence=minimum_confidence,
        pass_threshold=pass_threshold,
        fail_threshold=fail_threshold,
        dx=dx,
        dy=dy,
    )
    return PlacementMeasurement(
        dx=dx,
        dy=dy,
        distance=raw,
        normalized_distance=normalized,
        status=status,
        reason=reason,
        earlobe_confidence=earlobe.confidence,
        earring_confidence=earring.confidence,
        inside_zone=normalized <= fail_threshold,
    )


def reference_vector_from_points(
    earlobe_x: float,
    earlobe_y: float,
    earring_x: float,
    earring_y: float,
    ear_width: float,
    ear_height: float,
    zone_y_scale: float = 1.0,
) -> ReferenceVector:
    dx, dy = offset(earring_x, earring_y, earlobe_x, earlobe_y)
    magnitude = distance(dx, dy)
    return ReferenceVector(
        dx=dx,
        dy=dy,
        magnitude=magnitude,
        angle_degrees=direction_degrees(dx, dy),
        normalized_distance=normalize_distance(dx, dy, ear_width, zone_y_scale),
        ear_width=ear_width,
        ear_height=ear_height,
        earlobe_x=earlobe_x,
        earlobe_y=earlobe_y,
        earring_x=earring_x,
        earring_y=earring_y,
    )


def compare_reference(
    reference: ReferenceVector | None,
    actual: PlacementMeasurement,
    *,
    pass_threshold: float,
    fail_threshold: float,
    angle_fail_degrees: float = 35.0,
) -> ReferenceComparison:
    if reference is None:
        return ReferenceComparison(status="NOT_RUN", reason="No reference geometry is available.")
    if actual.dx is None or actual.dy is None or actual.normalized_distance is None:
        return ReferenceComparison(
            status="FAIL",
            magnitude_reference=reference.normalized_distance,
            reason="Actual placement could not be compared because an anchor is missing.",
        )
    actual_angle = direction_degrees(actual.dx, actual.dy)
    mag_error = abs(actual.normalized_distance - reference.normalized_distance)
    ang_error = angle_error(actual_angle, reference.angle_degrees)
    vec_error = vector_error(actual.dx, actual.dy, reference.dx, reference.dy)
    on_lobe = actual.normalized_distance <= pass_threshold
    direction_meaningful = reference.magnitude > 0.01 and not on_lobe
    if mag_error <= pass_threshold and (not direction_meaningful or ang_error <= angle_fail_degrees):
        status = "PASS"
        reason = "Actual relative placement matches the reference vector."
    elif mag_error <= fail_threshold and ang_error <= angle_fail_degrees * 1.5:
        status = "WARNING"
        reason = "Actual relative placement is close to the reference vector."
    else:
        status = "FAIL"
        reason = "Actual relative placement differs from the approved reference."
    return ReferenceComparison(
        status=status,
        magnitude_reference=reference.normalized_distance,
        magnitude_actual=actual.normalized_distance,
        distance_error=mag_error,
        angle_error=ang_error,
        vector_error=vec_error,
        reason=reason,
    )


def math_inf() -> float:
    return float("inf")
