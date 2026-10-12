"""Earlobe anchor estimation from MediaPipe face-mesh ear contours.

MediaPipe does not publish a dedicated earlobe landmark. The anchor is the
centroid of the lower portion of the ear contour, which corresponds to the lobe.
All landmark index lists live in this module.
"""

from __future__ import annotations

from app.cv.types import EarlobeAnchor, Landmark

# Person's anatomical left / right, matching MediaPipe face mesh.
LEFT_EAR_CONTOUR: tuple[int, ...] = (
    234, 227, 137, 177, 215, 138, 135, 169, 170, 140,
    171, 148, 176, 149, 150, 136, 172, 58, 132, 93,
)
RIGHT_EAR_CONTOUR: tuple[int, ...] = (
    454, 447, 366, 401, 435, 367, 364, 394, 395, 369,
    396, 377, 400, 378, 379, 365, 397, 288, 361, 323,
)

CONTOURS = {"left": LEFT_EAR_CONTOUR, "right": RIGHT_EAR_CONTOUR}
# Jaw-ear junction. On a front-facing mesh this sits on the lobe, while the
# lowest contour points continue down the jaw toward the chin.
LOBE_LANDMARK = {"left": 132, "right": 361}


class EarGeometryError(Exception):
    def __init__(self, message: str, missing: list[int] | None = None) -> None:
        super().__init__(message)
        self.missing = missing or []


class EarlobeAnchorEstimator:
    def __init__(self, min_points: int = 6, lower_fraction: float = 0.25) -> None:
        self.min_points = min_points
        self.lower_fraction = lower_fraction

    def estimate(
        self,
        landmarks: list[Landmark],
        side: str,
        *,
        min_ear_width: float = 0.012,
    ) -> EarlobeAnchor:
        if side not in CONTOURS:
            raise EarGeometryError(f"Unsupported ear side '{side}'.")
        if not landmarks:
            raise EarGeometryError(f"No landmarks available for the {side} ear.", missing=list(CONTOURS[side]))

        missing: list[int] = []
        points: list[Landmark] = []
        for index in CONTOURS[side]:
            if index >= len(landmarks):
                missing.append(index)
                continue
            landmark = landmarks[index]
            if landmark.x < -0.05 or landmark.x > 1.05 or landmark.y < -0.05 or landmark.y > 1.05:
                missing.append(index)
                continue
            points.append(landmark)

        if len(points) < self.min_points:
            raise EarGeometryError(
                f"Missing landmarks for the {side} ear contour.",
                missing=missing,
            )

        xs = [point.x for point in points]
        ys = [point.y for point in points]
        ear_width = max(xs) - min(xs)
        ear_height = max(ys) - min(ys)
        if ear_width < min_ear_width or ear_height < min_ear_width * 0.5:
            raise EarGeometryError(f"The {side} ear is not sufficiently visible.")

        lobe_index = LOBE_LANDMARK[side]
        lobe_point = landmarks[lobe_index] if lobe_index < len(landmarks) else None
        lobe_visible = (
            lobe_point is not None and -0.05 <= lobe_point.x <= 1.05 and -0.05 <= lobe_point.y <= 1.05
        )
        # A distant face makes the contour follow the jaw down to the chin.
        # The stud then sits on the jaw-ear landmark, just outside the mesh.
        if lobe_visible and ear_width < 0.08:
            nose_x = landmarks[1].x if len(landmarks) > 1 else sum(xs) / len(xs)
            direction = -1.0 if lobe_point.x <= nose_x else 1.0
            anchor_x = float(lobe_point.x + direction * 0.12 * ear_width)
            anchor_y = float(lobe_point.y)
        else:
            nose_x = landmarks[1].x if len(landmarks) > 1 else sum(xs) / len(xs)
            center_x = sum(xs) / len(xs)
            if center_x <= nose_x:
                outer_limit = min(xs) + 0.5 * ear_width
                outer = [point for point in points if point.x <= outer_limit]
            else:
                outer_limit = max(xs) - 0.5 * ear_width
                outer = [point for point in points if point.x >= outer_limit]
            outer = outer or points
            outer_ys = [point.y for point in outer]
            outer_height = max(outer_ys) - min(outer_ys)
            cutoff = max(outer_ys) - self.lower_fraction * max(outer_height, 1e-6)
            lower = [point for point in outer if point.y >= cutoff] or [max(outer, key=lambda point: point.y)]
            anchor_x = sum(point.x for point in lower) / len(lower)
            anchor_y = sum(point.y for point in lower) / len(lower)
        mean_confidence = sum(point.confidence for point in points) / len(points)
        spread_bonus = min(0.2, ear_width * 2.0)
        confidence = max(0.0, min(0.99, mean_confidence * 0.85 + spread_bonus))

        return EarlobeAnchor(
            side=side,
            x=float(anchor_x),
            y=float(anchor_y),
            confidence=float(confidence),
            ear_width=float(ear_width),
            ear_height=float(ear_height),
        )

    def visibility(self, landmarks: list[Landmark], side: str, min_ear_width: float = 0.012) -> bool:
        try:
            self.estimate(landmarks, side, min_ear_width=min_ear_width)
        except EarGeometryError:
            return False
        return True
