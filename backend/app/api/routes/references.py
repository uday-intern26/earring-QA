from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session

from app.api.dependencies import get_app_settings, get_db
from app.core.config import Settings
from app.schemas.reference import ReferenceAnchorUpdate, ReferenceRead
from app.services.reference_service import ReferenceService
from app.utils.files import ensure_within_data

router = APIRouter(prefix="/references", tags=["references"])


def _read(record, settings: Settings) -> ReferenceRead:
    payload = record.model_dump()
    payload["image_url"] = f"{settings.api_prefix}/references/{record.id}/image"
    return ReferenceRead.model_validate(payload)


@router.get("", response_model=list[ReferenceRead])
def list_references(
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> list[ReferenceRead]:
    return [_read(item, settings) for item in ReferenceService(settings).list(session)]


@router.post("/upload", response_model=ReferenceRead, status_code=201)
async def upload_reference(
    file: UploadFile = File(...),
    side: str = Form("left"),
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> ReferenceRead:
    if side not in {"left", "right"}:
        raise HTTPException(status_code=422, detail={"code": "INVALID_SIDE", "message": "Side must be left or right."})
    content = await file.read()
    try:
        record = ReferenceService(settings).save_upload(session, file.filename or "reference.png", content, side)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"code": "UNSUPPORTED_IMAGE", "message": str(exc)}) from exc
    return _read(record, settings)


@router.post("/{reference_id}/anchors", response_model=ReferenceRead)
def set_reference_anchors(
    reference_id: str,
    payload: ReferenceAnchorUpdate,
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> ReferenceRead:
    service = ReferenceService(settings)
    record = service.get(session, reference_id)
    if record is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Reference was not found."})
    updated = service.set_anchors(session, record, payload)
    return _read(updated, settings)


@router.get("/{reference_id}/image")
def reference_image(
    reference_id: str,
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> FileResponse:
    record = ReferenceService(settings).get(session, reference_id)
    if record is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Reference was not found."})
    path = ensure_within_data(Path(record.path))
    if not path.is_file():
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Reference file is missing."})
    return FileResponse(path)


@router.delete("/{reference_id}", status_code=204)
def delete_reference(
    reference_id: str,
    session: Session = Depends(get_db),
    settings: Settings = Depends(get_app_settings),
) -> None:
    service = ReferenceService(settings)
    record = service.get(session, reference_id)
    if record is None:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Reference was not found."})
    service.delete(session, record)
