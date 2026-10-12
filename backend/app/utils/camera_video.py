"""Turn an uploaded face video into the Y4M file Chromium uses as a fake camera."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import cv2
import numpy as np


def ensure_fake_camera(source: Path) -> Path:
    """Return a Y4M path Chromium can play as the webcam. Regenerates when the source changes."""
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError(source.name)
    if source.suffix.lower() == ".y4m" and " " not in str(source):
        return source
    destination = Path(tempfile.gettempdir()) / "aijewel-face-camera.y4m"
    if destination.is_file() and destination.stat().st_mtime >= source.stat().st_mtime and destination.stat().st_size > 0:
        return destination
    _write_y4m(source, destination)
    os.utime(destination, None)
    return destination


def _write_y4m(source: Path, destination: Path, *, max_frames: int = 150) -> None:
    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise ValueError(f"Face video could not be opened: {source.name}")
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width -= width % 2
    height -= height % 2
    fps = int(round(capture.get(cv2.CAP_PROP_FPS) or 25)) or 25
    if width < 2 or height < 2:
        capture.release()
        raise ValueError("Face video has no usable frames.")
    written = 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        handle.write(f"YUV4MPEG2 W{width} H{height} F{fps}:1 Ip A0:0 C420\n".encode("ascii"))
        while written < max_frames:
            ok, frame = capture.read()
            if not ok:
                break
            cropped = np.ascontiguousarray(frame[:height, :width])
            yuv = cv2.cvtColor(cropped, cv2.COLOR_BGR2YUV_I420)
            handle.write(b"FRAME\n")
            handle.write(yuv.tobytes())
            written += 1
    capture.release()
    if written == 0:
        destination.unlink(missing_ok=True)
        raise ValueError("Face video has no usable frames.")
