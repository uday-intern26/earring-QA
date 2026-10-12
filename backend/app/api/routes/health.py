from fastapi import APIRouter, Depends

from app.api.dependencies import get_app_settings
from app.core.config import Settings
from app.db.database import ping_database

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Settings = Depends(get_app_settings)) -> dict:
    database_ok = ping_database()
    return {
        "status": "ok" if database_ok else "degraded",
        "service": settings.app_name,
        "database": "ok" if database_ok else "unavailable",
        "applitools_enabled": settings.applitools_enabled,
    }
