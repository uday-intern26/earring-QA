"""Screenshot capture behind an adapter so storage can change later."""

from __future__ import annotations

from pathlib import Path

from app.adapters.browser_adapter import BrowserAdapter


class ScreenshotAdapter:
    def __init__(self, browser: BrowserAdapter) -> None:
        self.browser = browser

    async def capture(self, path: Path) -> Path:
        await self.browser.screenshot(path)
        return path
