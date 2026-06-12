from playwright.async_api import Page


class LoginPage:
    INPUT_USERNAME = "#user-name"
    INPUT_PASSWORD = "#password"
    BTN_LOGIN = "#login-button"
    ERROR_MESSAGE = "[data-test='error']"

    def __init__(self, page: Page):
        self.page = page

    async def navigate(self):
        await self.page.goto("https://www.saucedemo.com/")

    async def login(self, username: str, password: str):
        await self.page.fill(self.INPUT_USERNAME, username)
        await self.page.fill(self.INPUT_PASSWORD, password)
        await self.page.click(self.BTN_LOGIN)

    async def get_error_message(self) -> str:
        return await self.page.text_content(self.ERROR_MESSAGE) or ""
