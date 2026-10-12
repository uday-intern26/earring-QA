"""Frame quality measurements: blur, near-duplicate hashing, and image IO."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def read_bgr(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Unable to read image: {path.name}")
    return image


def bgr_to_rgb(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def blur_variance(image_bgr: np.ndarray) -> float:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def blur_score(image_bgr: np.ndarray, norm_variance: float) -> float:
    if norm_variance <= 0:
        return 0.0
    return float(max(0.0, min(1.0, blur_variance(image_bgr) / norm_variance)))


def average_hash(image_bgr: np.ndarray, size: int = 8) -> np.ndarray:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA)
    return (small > small.mean()).astype(np.uint8).flatten()


def hamming(left: np.ndarray, right: np.ndarray) -> int:
    return int(np.count_nonzero(left != right))


def perceptual_hash(image_bgr: np.ndarray, hash_size: int = 8) -> np.ndarray:
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA)
    dct = cv2.dct(np.float32(resized))
    low = dct[:hash_size, :hash_size]
    median = np.median(low)
    return (low > median).astype(np.uint8).flatten()


def ssim_score(left_bgr: np.ndarray, right_bgr: np.ndarray) -> float:
    """Mean structural similarity. Used only as a secondary visual metric."""
    left = cv2.cvtColor(left_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    right = cv2.cvtColor(right_bgr, cv2.COLOR_BGR2GRAY).astype(np.float64)
    height = min(left.shape[0], right.shape[0])
    width = min(left.shape[1], right.shape[1])
    if height < 16 or width < 16:
        return 0.0
    left = cv2.resize(left, (width, height))
    right = cv2.resize(right, (width, height))
    kernel = (11, 11)
    mu_left = cv2.GaussianBlur(left, kernel, 1.5)
    mu_right = cv2.GaussianBlur(right, kernel, 1.5)
    mu_left_sq = mu_left * mu_left
    mu_right_sq = mu_right * mu_right
    mu_cross = mu_left * mu_right
    sigma_left = cv2.GaussianBlur(left * left, kernel, 1.5) - mu_left_sq
    sigma_right = cv2.GaussianBlur(right * right, kernel, 1.5) - mu_right_sq
    sigma_cross = cv2.GaussianBlur(left * right, kernel, 1.5) - mu_cross
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    numerator = (2 * mu_cross + c1) * (2 * sigma_cross + c2)
    denominator = (mu_left_sq + mu_right_sq + c1) * (sigma_left + sigma_right + c2)
    score = numerator / (denominator + 1e-8)
    return float(max(0.0, min(1.0, score.mean())))


def absdiff_score(left_bgr: np.ndarray, right_bgr: np.ndarray) -> float:
    height = min(left_bgr.shape[0], right_bgr.shape[0])
    width = min(left_bgr.shape[1], right_bgr.shape[1])
    left = cv2.resize(left_bgr, (width, height))
    right = cv2.resize(right_bgr, (width, height))
    return float(np.mean(cv2.absdiff(left, right)) / 255.0)
