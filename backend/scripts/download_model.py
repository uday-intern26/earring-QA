"""Download the MediaPipe face landmarker used for earlobe estimation."""

from pathlib import Path
import urllib.request

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)


def main() -> None:
    destination = Path(__file__).resolve().parents[1] / "models" / "face_landmarker.task"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_file() and destination.stat().st_size > 0:
        print(f"Model already present at {destination}")
        return
    print(f"Downloading {MODEL_URL}")
    urllib.request.urlretrieve(MODEL_URL, destination)
    print(f"Saved {destination}")


if __name__ == "__main__":
    main()
