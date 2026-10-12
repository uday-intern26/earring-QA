"""Create the local sample reference image and try-on video used by integration tests."""

from pathlib import Path

import cv2
import numpy as np

FIXTURES = Path(__file__).resolve().parent


def _frame_image(index: int) -> np.ndarray:
    palette = [
        (18, 22, 90),
        (90, 22, 18),
        (18, 90, 22),
        (90, 90, 18),
        (18, 90, 90),
        (90, 18, 90),
        (40, 40, 40),
        (120, 50, 20),
    ]
    image = np.zeros((240, 320, 3), dtype=np.uint8)
    image[:] = palette[index % len(palette)]
    cv2.rectangle(image, (12, 12), (308, 228), (240, 240, 240), 2)
    cv2.rectangle(image, (20 + index * 28, 24), (110 + index * 28, 110), (40, 40 + index * 20, 200), -1)
    cv2.ellipse(image, (110, 120), (22, 48), 0, 0, 360, (90, 160, 220), -1)
    cv2.circle(image, (110, 156), 4, (40, 220, 80), -1)
    cv2.circle(image, (112, 162), 3, (50, 50, 230), -1)
    cv2.putText(image, f"F{index}", (40, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
    cv2.line(image, (20, 30 + index * 12), (300, 200 - index * 10), (0, 220, 180), 2)
    return image


def write_reference(path: Path | None = None) -> Path:
    target = path or (FIXTURES / "sample_reference.png")
    cv2.imwrite(str(target), _frame_image(0))
    return target


def write_video(path: Path | None = None, frames: int = 8) -> Path:
    target = path or (FIXTURES / "sample_tryon.mp4")
    candidates = [(target, "mp4v"), (target.with_suffix(".avi"), "MJPG")]
    for dest, codec in candidates:
        writer = cv2.VideoWriter(str(dest), cv2.VideoWriter_fourcc(*codec), 5, (320, 240))
        if not writer.isOpened():
            continue
        for index in range(frames):
            writer.write(_frame_image(index))
        writer.release()
        capture = cv2.VideoCapture(str(dest))
        readable = capture.isOpened() and capture.read()[0]
        capture.release()
        if readable:
            if dest != target and dest.exists() and not target.exists():
                dest.replace(target)
            return target if target.exists() else dest
    raise RuntimeError("OpenCV could not write a readable sample video on this machine.")


if __name__ == "__main__":
    print(write_reference())
    print(write_video())
