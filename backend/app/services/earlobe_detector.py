"""Layer 2 earlobe detection. Landmark indices stay inside ear geometry."""

from __future__ import annotations

from app.cv.ear_geometry import EarlobeAnchorEstimator, EarGeometryError
from app.cv.types import EarlobeAnchor, FaceLandmarkResult


class EarlobeDetector:
    def __init__(self, min_ear_width: float = 0.012) -> None:
        self.min_ear_width = min_ear_width
        self._estimator = EarlobeAnchorEstimator()

    def detect(self, face: FaceLandmarkResult | None, side: str) -> tuple[EarlobeAnchor | None, str | None]:
        if face is None or not face.face_detected or not face.landmarks:
            return None, f"Unable to detect the {side} earlobe because the face was not found."
        try:
            anchor = self._estimator.estimate(face.landmarks, side, min_ear_width=self.min_ear_width)
        except EarGeometryError as exc:
            return None, str(exc)
        return anchor, None
