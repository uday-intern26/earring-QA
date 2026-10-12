"""Threshold checks shared by placement and temporal stages."""

from __future__ import annotations


def classify_placement(
    normalized_distance: float,
    confidence: float,
    *,
    minimum_confidence: float,
    pass_threshold: float,
    fail_threshold: float,
    dy: float = 0.0,
    dx: float = 0.0,
    missing_earlobe: bool = False,
    missing_earring: bool = False,
) -> tuple[str, str]:
    if missing_earlobe:
        return "FAIL", "Earlobe anchor could not be detected."
    if missing_earring:
        return "FAIL", "Earring attachment anchor could not be detected."
    if confidence < minimum_confidence:
        return (
            "FAIL",
            f"Confidence {confidence:.2f} is below the minimum {minimum_confidence:.2f}.",
        )
    if normalized_distance <= pass_threshold:
        return "PASS", "Earring attachment point is inside the earlobe placement zone."
    if normalized_distance <= fail_threshold:
        return "WARNING", "Earring attachment point is near the edge of the earlobe placement zone."
    if abs(dy) >= abs(dx) and dy > 0:
        return "FAIL", "Earring attachment point is below the configured earlobe placement zone."
    if abs(dy) >= abs(dx) and dy < 0:
        return "FAIL", "Earring attachment point is above the configured earlobe placement zone."
    return "FAIL", "Earring attachment point is outside the configured earlobe placement zone."


def assert_thresholds(pass_threshold: float, fail_threshold: float, minimum_pass_rate: float) -> None:
    if pass_threshold < 0 or fail_threshold < 0:
        raise ValueError("Thresholds must be non-negative.")
    if fail_threshold < pass_threshold:
        raise ValueError("Fail threshold must be greater than or equal to the pass threshold.")
    if not 0 <= minimum_pass_rate <= 1:
        raise ValueError("Minimum pass rate must be between 0 and 1.")
