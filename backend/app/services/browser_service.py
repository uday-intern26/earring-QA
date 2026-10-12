"""Opens the public try-on application and checks that login reaches the app."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from app.adapters.tryon_application import PlaywrightTryOnAdapter, TryOnError
from app.core.config import Settings
from app.core.logging import log_event
from app.core.security import secret_registry
from app.models.application import Application
from app.schemas.application import ApplicationValidateResponse, CheckItem


def validate_url(url: str) -> None:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise TryOnError(
            "Invalid URL. Enter an http or https address such as the public Amplify URL.",
            "INVALID_URL",
        )
    if parsed.username or parsed.password:
        raise TryOnError("Do not embed credentials in the application URL.", "INVALID_URL")


class BrowserService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def validate(
        self,
        *,
        url: str,
        username: str,
        password: str,
        username_selector: str | None,
        password_selector: str | None,
        submit_selector: str | None,
        ready_selector: str | None,
        screenshot_dir: Path,
        video_path: str | None = None,
    ) -> ApplicationValidateResponse:
        checks: list[CheckItem] = []
        secret_registry.add(password)
        try:
            validate_url(url)
            checks.append(CheckItem(name="url_format", ok=True, detail="URL format is valid."))
        except TryOnError as exc:
            checks.append(CheckItem(name="url_format", ok=False, detail=str(exc)))
            return _failed(checks, str(exc))

        face_video = Path(video_path) if video_path else None
        if face_video is None or not face_video.is_file():
            checks.append(
                CheckItem(
                    name="face_video",
                    ok=False,
                    detail="Upload a video of the girl wearing no earrings before validation.",
                )
            )
            return _failed(
                checks,
                "Upload a video of the girl wearing no earrings, then validate the try-on again.",
            )
        checks.append(CheckItem(name="face_video", ok=True, detail="Face video is ready for the try-on camera."))
        application = Application(
            id="validation",
            name="validation",
            type="web",
            url=url,
            video_path=str(face_video),
            username=username or None,
            username_selector=username_selector,
            password_selector=password_selector,
            submit_selector=submit_selector,
            ready_selector=ready_selector,
        )
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        shot = screenshot_dir / f"{uuid4().hex}.png"
        adapter = PlaywrightTryOnAdapter(
            application,
            username=username,
            password=password,
            output_dir=screenshot_dir,
            fps=1,
            duration_seconds=1,
            headless=self.settings.playwright_headless,
            viewport_width=self.settings.viewport_width,
            viewport_height=self.settings.viewport_height,
            timeout_ms=self.settings.navigation_timeout_ms,
        )
        reachable = False
        login_ok = False
        loaded = False
        try:
            await adapter.connect()
            reachable = True
            checks.append(CheckItem(name="reachable", ok=True, detail="Application is reachable."))
            await adapter.authenticate()
            login_ok = True
            checks.append(CheckItem(name="login", ok=True, detail="Login successful."))
            await adapter.launch()
            loaded = True
            checks.append(CheckItem(name="loaded", ok=True, detail="Try-on application loaded."))
            jewelry = await adapter.catalog_earring_names()
            if not jewelry:
                checks.append(
                    CheckItem(name="catalog", ok=False, detail="The try-on catalog did not list any earrings.")
                )
                return ApplicationValidateResponse(
                    status="failed",
                    reachable=True,
                    login_successful=True,
                    application_loaded=True,
                    message="The try-on opened, but no catalog earrings were available to choose.",
                    checks=checks,
                )
            checks.append(
                CheckItem(name="catalog", ok=True, detail=f"{len(jewelry)} catalog earrings are ready to test.")
            )
            try:
                await adapter.browser.screenshot(shot)
                screenshot = str(shot)
            except Exception:
                screenshot = None
            log_event("APPLICATION_VALIDATED", url=url, jewelry=len(jewelry))
            return ApplicationValidateResponse(
                status="success",
                reachable=True,
                login_successful=True,
                application_loaded=True,
                message="Try-on is open. Choose the earring to test on the girl in the video.",
                checks=checks,
                screenshot_url=screenshot,
                jewelry=jewelry,
            )
        except TryOnError as exc:
            if not reachable:
                checks.append(CheckItem(name="reachable", ok=False, detail=str(exc)))
            elif not login_ok:
                checks.append(CheckItem(name="login", ok=False, detail=str(exc)))
            elif not loaded:
                checks.append(CheckItem(name="loaded", ok=False, detail=str(exc)))
            else:
                checks.append(CheckItem(name="catalog", ok=False, detail=str(exc)))
            log_event("APPLICATION_VALIDATION_FAILED", code=exc.code, detail=str(exc))
            return ApplicationValidateResponse(
                status="failed",
                reachable=reachable,
                login_successful=login_ok,
                application_loaded=loaded,
                message=str(exc),
                checks=checks,
                screenshot_url=None,
            )
        except Exception as exc:
            detail = secret_registry.redact(str(exc)).strip() or exc.__class__.__name__
            message = f"Browser automation failed: {detail}"
            checks.append(CheckItem(name="browser", ok=False, detail=message))
            log_event("APPLICATION_VALIDATION_FAILED", code="BROWSER", detail=message)
            return _failed(checks, message)
        finally:
            await adapter.close()
            secret_registry.discard(password)


def _failed(checks: list[CheckItem], message: str) -> ApplicationValidateResponse:
    return ApplicationValidateResponse(
        status="failed",
        reachable=False,
        login_successful=False,
        application_loaded=False,
        message=message,
        checks=checks,
    )
