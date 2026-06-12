from typing import Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    APIRequestContext,
    async_playwright,
)


class PlaywrightDriver:
    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    async def start(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def create_context(self) -> BrowserContext:
        if not self._browser:
            raise RuntimeError("Browser not started. Call start() first.")
        return await self._browser.new_context()

    async def create_page(self, context: Optional[BrowserContext] = None) -> Page:
        if context:
            return await context.new_page()
        ctx = await self.create_context()
        return await ctx.new_page()

    async def create_api_context(
        self, base_url: str, headers: Optional[dict] = None
    ) -> APIRequestContext:
        if not self._playwright:
            raise RuntimeError("Playwright not started. Call start() first.")
        return await self._playwright.request.new_context(
            base_url=base_url, extra_http_headers=headers
        )
