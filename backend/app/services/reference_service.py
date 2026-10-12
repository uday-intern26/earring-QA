"""Reference image storage and relative-placement analysis."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from sqlmodel import Session, select

from app.core.config import Settings
from app.cv.anchor_geometry import reference_vector_from_points
from app.cv.face_landmarks import FaceLandmarkError, MediaPipeFaceLandmarker
from app.cv.image_processing import bgr_to_rgb, read_bgr
from app.db.database import allocate_id
from app.models.reference import ReferenceImage
from app.schemas.reference import ReferenceAnchorUpdate
from app.services.earlobe_detector import EarlobeDetector
from app.services.earring_detector import FallbackEarringAnchorDetector
from app.utils.files import safe_filename

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


class ReferenceService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._landmarker: MediaPipeFaceLandmarker | None = None

    def list(self, session: Session) -> list[ReferenceImage]:
        return list(session.exec(select(ReferenceImage).order_by(ReferenceImage.created_at.desc())).all())

    def get(self, session: Session, reference_id: str) -> ReferenceImage | None:
        return session.get(ReferenceImage, reference_id)

    def delete(self, session: Session, reference: ReferenceImage) -> None:
        path = Path(reference.path)
        if path.is_file():
            path.unlink()
        session.delete(reference)
        session.commit()

    def save_upload(self, session: Session, filename: str, content: bytes, side: str = "left") -> ReferenceImage:
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise ValueError("Unsupported image. Upload PNG, JPG, JPEG, or WEBP.")
        if len(content) > self.settings.max_upload_bytes:
            raise ValueError("Reference image exceeds the upload size limit.")
        reference_id = allocate_id(session, "REF", ReferenceImage)
        destination = self.settings.data_dir / "references" / f"{reference_id}{extension}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        try:
            with Image.open(destination) as image:
                image.verify()
            with Image.open(destination) as image:
                width, height = image.size
        except (UnidentifiedImageError, OSError) as exc:
            destination.unlink(missing_ok=True)
            raise ValueError("The uploaded file is not a readable image.") from exc

        record = ReferenceImage(
            id=reference_id,
            filename=safe_filename(filename),
            path=str(destination),
            width=width,
            height=height,
            side=side,
        )
        self._analyze(record, side)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    def set_anchors(self, session: Session, record: ReferenceImage, payload: ReferenceAnchorUpdate) -> ReferenceImage:
        vector = reference_vector_from_points(
            payload.earlobe_x,
            payload.earlobe_y,
            payload.earring_x,
            payload.earring_y,
            payload.ear_width,
            payload.ear_height,
            self.settings.default_zone_y_scale,
        )
        record.side = payload.side
        record.earlobe_x = payload.earlobe_x
        record.earlobe_y = payload.earlobe_y
        record.earring_x = payload.earring_x
        record.earring_y = payload.earring_y
        record.ear_width = payload.ear_width
        record.ear_height = payload.ear_height
        record.vector_dx = vector.dx
        record.vector_dy = vector.dy
        record.normalized_distance = vector.normalized_distance
        record.confidence = 1.0
        record.analysis_error = None
        record.analysis_json = json.dumps({"source": "manual", "vector": vector.model_dump()})
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

    def _analyze(self, record: ReferenceImage, side: str) -> None:
        try:
            image = read_bgr(Path(record.path))
            face = self._faces().detect(bgr_to_rgb(image))
            earlobe, error = EarlobeDetector(self.settings.min_ear_width).detect(face, side)
            if earlobe is None:
                record.analysis_error = error or "Unable to estimate the reference earlobe."
                return
            earring = FallbackEarringAnchorDetector().detect(image, earlobe, side=side)
            if earring.x is None or earring.y is None:
                record.earlobe_x = earlobe.x
                record.earlobe_y = earlobe.y
                record.ear_width = earlobe.ear_width
                record.ear_height = earlobe.ear_height
                record.confidence = earlobe.confidence
                record.analysis_error = earring.reason
                return
            vector = reference_vector_from_points(
                earlobe.x,
                earlobe.y,
                earring.x,
                earring.y,
                earlobe.ear_width,
                earlobe.ear_height,
                self.settings.default_zone_y_scale,
            )
            record.side = side
            record.earlobe_x = earlobe.x
            record.earlobe_y = earlobe.y
            record.earring_x = earring.x
            record.earring_y = earring.y
            record.ear_width = earlobe.ear_width
            record.ear_height = earlobe.ear_height
            record.vector_dx = vector.dx
            record.vector_dy = vector.dy
            record.normalized_distance = vector.normalized_distance
            record.confidence = min(earlobe.confidence, earring.confidence)
            record.analysis_error = None
            record.analysis_json = json.dumps(
                {"source": earring.source, "vector": vector.model_dump(), "earring_confidence": earring.confidence}
            )
        except FaceLandmarkError as exc:
            record.analysis_error = str(exc)
        except Exception as exc:
            record.analysis_error = f"Reference analysis failed: {exc}"

    def _faces(self) -> MediaPipeFaceLandmarker:
        if self._landmarker is None:
            self._landmarker = MediaPipeFaceLandmarker(self.settings.resolved_face_model_path)
        return self._landmarker
