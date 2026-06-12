from typing import Optional

from playwright.async_api import Page, Locator


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    async def navigate(self, url: str) -> None:
        await self.page.goto(url)

    async def click(self, selector: str, timeout: int = 30000) -> None:
        await self.page.click(selector, timeout=timeout)

    async def fill(self, selector: str, value: str, timeout: int = 30000) -> None:
        await self.page.fill(selector, value, timeout=timeout)

    async def wait_for(
        self, selector: str, state: str = "visible", timeout: int = 30000
    ) -> Locator:
        locator = self.page.locator(selector)
        await locator.wait_for(state=state, timeout=timeout)
        return locator

    async def get_text(self, selector: str, timeout: int = 30000) -> str:
        locator = await self.wait_for(selector, timeout=timeout)
        return await locator.text_content() or ""

    async def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        try:
            await self.page.wait_for_selector(
                selector, state="visible", timeout=timeout
            )
            return True
        except Exception:
            return False

    async def screenshot(self, name: str) -> bytes:
        return await self.page.screenshot(name=name)

    async def get_url(self) -> str:
        return self.page.url

    async def get_attribute(
        self, selector: str, attribute: str, timeout: int = 30000
    ) -> Optional[str]:
        locator = await self.wait_for(selector, timeout=timeout)
        return await locator.get_attribute(attribute)

    async def select_option(self, selector: str, value: str) -> None:
        await self.page.select_option(selector, value)

    async def hover(self, selector: str) -> None:
        await self.page.hover(selector)

    async def press_key(self, selector: str, key: str) -> None:
        await self.page.press(selector, key)
