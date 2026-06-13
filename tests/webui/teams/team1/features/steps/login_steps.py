from behave import step
from allure import attach
from allure_commons.types import AttachmentType
from tests.webui.teams.team1.pages.login_page import LoginPage
from playwright.async_api import async_playwright


async def _ensure_page(context):
    if not hasattr(context, "page") or context.page is None:
        context._playwright = await async_playwright().start()
        context._browser = await context._playwright.chromium.launch(headless=True)
        context._browser_context = await context._browser.new_context()
        context.page = await context._browser_context.new_page()


@step("the user is on the login page")
async def step_navigate(context):
    await _ensure_page(context)
    context.login_page = LoginPage(context.page)
    await context.login_page.navigate()
    attach("Navigated to SauceDemo login page", name="Step Info", attachment_type=AttachmentType.TEXT)


@step('the user enters username "{username}" and password "{password}"')
async def step_enter_credentials(context, username, password):
    await context.login_page.login(username, password)
    attach(f"Credentials entered: {username}", name="Step Info", attachment_type=AttachmentType.TEXT)


@step("the user clicks the login button")
async def step_click_login(context):
    attach("Login button clicked", name="Step Info", attachment_type=AttachmentType.TEXT)


@step("the user should see the inventory page")
async def step_verify_inventory(context):
    current_url = context.page.url
    attach(f"Current URL: {current_url}", name="Response", attachment_type=AttachmentType.TEXT)
    assert "/inventory.html" in current_url


@step('the user should see an error message "{message}"')
async def step_verify_error(context, message):
    error = await context.login_page.get_error_message()
    attach(f"Error message: {error}", name="Response", attachment_type=AttachmentType.TEXT)
    assert message in error
