"""MediaPipe Face Landmarker wrapper.

The Tasks API does not emit a reliable per-landmark visibility score for face mesh.
In-frame landmarks are treated as usable, and anatomical confidence is refined by
the earlobe estimator from ear-contour geometry.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from app.cv.types import FaceLandmarkResult, HeadPose, Landmark


class FaceLandmarkError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.recommended_action = (
            "Download the face landmarker model with backend/scripts/download_model.py, "
            "or set FACE_MODEL_PATH to an existing face_landmarker.task file."
        )


def _euler_from_matrix(matrix: np.ndarray) -> HeadPose:
    rotation = np.array(matrix, dtype=float).reshape(4, 4)[:3, :3]
    sy = math.sqrt(rotation[0, 0] ** 2 + rotation[1, 0] ** 2)
    pitch = math.degrees(math.atan2(-rotation[2, 0], sy if sy > 1e-8 else 1e-8))
    yaw = math.degrees(math.atan2(rotation[1, 0], rotation[0, 0]))
    roll = math.degrees(math.atan2(rotation[2, 1], rotation[2, 2]))
    return HeadPose(yaw=yaw, pitch=pitch, roll=roll)


def _landmark_confidence(raw) -> float:
    presence = float(getattr(raw, "presence", 0.0) or 0.0)
    visibility = float(getattr(raw, "visibility", 0.0) or 0.0)
    if presence > 0:
        return presence
    if visibility > 0:
        return visibility
    x = float(raw.x)
    y = float(raw.y)
    if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
        return 1.0
    return 0.0


class MediaPipeFaceLandmarker:
    def __init__(self, model_path: Path) -> None:
        self.model_path = Path(model_path)
        self._landmarker = None

    def _load(self):
        if self._landmarker is not None:
            return self._landmarker
        if not self.model_path.is_file():
            raise FaceLandmarkError(
                "Face landmarker model is missing at "
                f"{self.model_path}. Run backend/scripts/download_model.py."
            )
        try:
            import mediapipe as mp
            from mediapipe.tasks.python import BaseOptions
            from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions
        except ImportError as exc:
            raise FaceLandmarkError("MediaPipe is not installed.") from exc

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(self.model_path)),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=True,
        )
        self._landmarker = FaceLandmarker.create_from_options(options)
        return self._landmarker

    def detect(self, image_rgb: np.ndarray) -> FaceLandmarkResult:
        landmarker = self._load()
        import mediapipe as mp

        if image_rgb.ndim != 3 or image_rgb.shape[2] != 3:
            raise FaceLandmarkError("Face landmarker expects an RGB image.")
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(image_rgb))
        result = landmarker.detect(mp_image)
        if not result.face_landmarks:
            return FaceLandmarkResult(face_detected=False, reason="face_not_detected")

        raw_landmarks = result.face_landmarks[0]
        landmarks = [
            Landmark(x=float(item.x), y=float(item.y), z=float(item.z), confidence=_landmark_confidence(item))
            for item in raw_landmarks
        ]
        pose = None
        matrices = getattr(result, "facial_transformation_matrixes", None) or []
        if matrices:
            pose = _euler_from_matrix(np.array(matrices[0]))
        mean_confidence = sum(item.confidence for item in landmarks) / max(len(landmarks), 1)
        return FaceLandmarkResult(
            face_detected=True,
            landmarks=landmarks,
            confidence=float(mean_confidence),
            head_pose=pose,
        )

    def close(self) -> None:
        if self._landmarker is not None:
            close = getattr(self._landmarker, "close", None)
            if close:
                close()
            self._landmarker = None
