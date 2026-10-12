"""AIJewel earring earlobe-alignment QA API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.adapters.tryon_application import TryOnError
from app.api.routes import applications, execution, health, references, results, tests
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.database import init_db
from app.utils.files import StorageError


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    settings.ensure_dirs()
    init_db()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="AIJewel Earring QA",
        summary="Local earlobe alignment QA for the AIJewel virtual try-on.",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(settings.frontend_url)

    prefix = settings.api_prefix
    app.include_router(health.router, prefix=prefix)
    app.include_router(applications.router, prefix=prefix)
    app.include_router(references.router, prefix=prefix)
    app.include_router(tests.router, prefix=prefix)
    app.include_router(execution.router, prefix=prefix)
    app.include_router(results.router, prefix=prefix)

    @app.exception_handler(TryOnError)
    async def tryon_error(_request: Request, exc: TryOnError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "detail": {
                    "code": exc.code,
                    "message": str(exc),
                    "recommended_action": exc.recommended_action,
                }
            },
        )

    @app.exception_handler(StorageError)
    async def storage_error(_request: Request, exc: StorageError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": {"code": exc.code, "message": str(exc)}})

    return app


app = create_app()
