"""Secondary visual comparison. It never decides anatomical alignment."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from app.core.config import Settings
from app.cv.image_processing import absdiff_score, hamming, perceptual_hash, read_bgr, ssim_score


class ComparisonService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def compare_local(self, reference_path: Path | None, actual_path: Path | None) -> dict:
        if reference_path is None or actual_path is None:
            return {"method": "local", "status": "NOT_RUN", "reason": "Reference or actual image is missing."}
        try:
            reference = read_bgr(reference_path)
            actual = read_bgr(actual_path)
        except ValueError as exc:
            return {"method": "local", "status": "FAIL", "reason": str(exc)}
        hash_distance = hamming(perceptual_hash(reference), perceptual_hash(actual))
        return {
            "method": "local",
            "status": "INFO",
            "ssim": ssim_score(reference, actual),
            "perceptual_hash_distance": hash_distance,
            "mean_absolute_difference": absdiff_score(reference, actual),
            "reason": "Local visual metrics are informational and do not decide earlobe alignment.",
        }

    def compare_applitools(self, image_path: Path | None, test_name: str) -> dict:
        if not self.settings.applitools_enabled:
            return {"method": "applitools", "status": "SKIPPED", "reason": "Applitools is disabled."}
        if not self.settings.applitools_api_key:
            return {
                "method": "applitools",
                "status": "SKIPPED",
                "reason": "Applitools is enabled but APPLITOOLS_API_KEY is empty.",
            }
        if image_path is None:
            return {"method": "applitools", "status": "SKIPPED", "reason": "No image was available."}
        try:
            from applitools.images import Eyes
        except ImportError:
            return {
                "method": "applitools",
                "status": "SKIPPED",
                "reason": "The applitools images package is not installed. Anatomical QA continues.",
            }
        try:
            import cv2

            image = cv2.imread(str(image_path))
            if image is None:
                return {"method": "applitools", "status": "ERROR", "reason": "Unable to read the comparison image."}
            eyes = Eyes()
            eyes.api_key = self.settings.applitools_api_key
            if self.settings.applitools_server_url:
                eyes.server_url = self.settings.applitools_server_url
            eyes.open("AIJewel QA", test_name)
            eyes.check_image(image)
            eyes.close(False)
            return {
                "method": "applitools",
                "status": "RECORDED",
                "reason": "Screenshot was sent to Applitools. Anatomical alignment still comes from anchors.",
            }
        except Exception as exc:
            return {
                "method": "applitools",
                "status": "ERROR",
                "reason": f"Applitools call failed: {exc}",
            }


def mean_image(images: list[np.ndarray]) -> np.ndarray | None:
    if not images:
        return None
    return images[0]
