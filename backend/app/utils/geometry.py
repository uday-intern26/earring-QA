"""Reusable geometry. Placement decisions use normalized coordinates, never raw pixels."""

from __future__ import annotations

import math


def offset(earring_x: float, earring_y: float, earlobe_x: float, earlobe_y: float) -> tuple[float, float]:
    return earring_x - earlobe_x, earring_y - earlobe_y


def distance(dx: float, dy: float) -> float:
    return math.hypot(dx, dy)


def normalize_distance(dx: float, dy: float, ear_width: float, zone_y_scale: float = 1.0) -> float:
    """Distance divided by ear width.

    zone_y_scale stretches the vertical axis of the placement ellipse.
    At 1.0 the value matches hypot(dx, dy) / ear_width.
    """
    if ear_width <= 1e-8:
        return math.inf
    scale = zone_y_scale if zone_y_scale > 1e-8 else 1.0
    return math.hypot(dx / ear_width, dy / (ear_width * scale))


def direction_degrees(dx: float, dy: float) -> float:
    return math.degrees(math.atan2(dy, dx))


def angle_error(angle_a: float, angle_b: float) -> float:
    delta = abs(angle_a - angle_b) % 360.0
    return min(delta, 360.0 - delta)


def vector_error(dx_a: float, dy_a: float, dx_b: float, dy_b: float) -> float:
    return math.hypot(dx_a - dx_b, dy_a - dy_b)


def point_in_ellipse(
    dx: float,
    dy: float,
    ear_width: float,
    max_normalized_distance: float,
    zone_y_scale: float = 1.0,
) -> bool:
    if max_normalized_distance < 0:
        return False
    return normalize_distance(dx, dy, ear_width, zone_y_scale) <= max_normalized_distance + 1e-9


def ellipse_radii(
    ear_width: float,
    threshold: float,
    zone_y_scale: float = 1.0,
) -> tuple[float, float]:
    """Normalized radii of the placement ellipse (x to the right, y downward)."""
    radius_x = threshold * ear_width
    radius_y = threshold * ear_width * zone_y_scale
    return radius_x, radius_y
