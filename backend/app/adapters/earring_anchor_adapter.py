"""Reads the preferred AIJewel earring anchor from the live try-on page."""

from __future__ import annotations

from app.adapters.browser_adapter import BrowserAdapter

_SCRIPT = """
async () => {
  const pages = [window];
  const frame = document.querySelector('iframe');
  try {
    if (frame && frame.contentWindow) pages.push(frame.contentWindow);
  } catch (error) {
    // A cross-origin try-on frame has no readable debug state.
  }
  for (const page of pages) {
    const bridged = page.__AIJEWEL_QA__ || page.AIJewelQA || null;
    if (bridged) return bridged;
  }
  const paths = ['/debug/tryon-state', '/api/debug/tryon-state'];
  for (const path of paths) {
    try {
      const response = await fetch(path, { credentials: 'include' });
      const contentType = response.headers.get('content-type') || '';
      if (response.ok && contentType.includes('json')) {
        return await response.json();
      }
    } catch (error) {
      continue;
    }
  }
  return null;
}
"""


class EarringAnchorPageAdapter:
    def __init__(self, browser: BrowserAdapter) -> None:
        self.browser = browser

    async def read_state(self) -> dict | None:
        state = await self.browser.evaluate(_SCRIPT)
        if isinstance(state, dict):
            return state
        return None
