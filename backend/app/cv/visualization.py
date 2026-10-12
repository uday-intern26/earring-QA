"""Draw geometry overlays. Colors are supplied by configuration, not chosen here."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from app.cv.types import EarlobeAnchor, EarringAnchor
from app.utils.geometry import ellipse_radii


def hex_to_bgr(value: str) -> tuple[int, int, int]:
    cleaned = value.strip().lstrip("#")
    if len(cleaned) != 6:
        return (255, 255, 255)
    red = int(cleaned[0:2], 16)
    green = int(cleaned[2:4], 16)
    blue = int(cleaned[4:6], 16)
    return (blue, green, red)


class OverlayPalette:
    def __init__(self, earlobe: str, earring: str, zone: str, inner_zone: str, vector: str) -> None:
        self.earlobe = hex_to_bgr(earlobe)
        self.earring = hex_to_bgr(earring)
        self.zone = hex_to_bgr(zone)
        self.inner_zone = hex_to_bgr(inner_zone)
        self.vector = hex_to_bgr(vector)


def annotate_frame(
    image_bgr: np.ndarray,
    earlobe: EarlobeAnchor | None,
    earring: EarringAnchor | None,
    *,
    palette: OverlayPalette,
    pass_threshold: float,
    fail_threshold: float,
    zone_y_scale: float = 1.0,
    normalized_distance: float | None = None,
) -> np.ndarray:
    canvas = image_bgr.copy()
    height, width = canvas.shape[:2]
    if earlobe is None:
        return canvas

    center = (int(earlobe.x * width), int(earlobe.y * height))
    outer_rx, outer_ry = ellipse_radii(earlobe.ear_width, fail_threshold, zone_y_scale)
    inner_rx, inner_ry = ellipse_radii(earlobe.ear_width, pass_threshold, zone_y_scale)
    outer_axes = (max(4, int(outer_rx * width)), max(4, int(outer_ry * height)))
    inner_axes = (max(3, int(inner_rx * width)), max(3, int(inner_ry * height)))
    cv2.ellipse(canvas, center, outer_axes, 0, 0, 360, palette.zone, 2)
    cv2.ellipse(canvas, center, inner_axes, 0, 0, 360, palette.inner_zone, 1)
    cv2.circle(canvas, center, 6, palette.earlobe, -1)

    if earring and earring.x is not None and earring.y is not None:
        earring_point = (int(earring.x * width), int(earring.y * height))
        cv2.line(canvas, center, earring_point, palette.vector, 2)
        cv2.circle(canvas, earring_point, 6, palette.earring, -1)
        if normalized_distance is not None and math_isfinite(normalized_distance):
            label_x = int((center[0] + earring_point[0]) / 2) + 8
            label_y = int((center[1] + earring_point[1]) / 2)
            cv2.putText(
                canvas,
                f"{normalized_distance:.3f}",
                (label_x, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                palette.vector,
                1,
                cv2.LINE_AA,
            )
    return canvas


def save_image(path: Path, image_bgr: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image_bgr):
        raise ValueError(f"Unable to write image {path.name}")


def math_isfinite(value: float) -> bool:
    return value == value and value not in (float("inf"), float("-inf"))
