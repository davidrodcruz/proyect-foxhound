from behave import step
from allure import attach
from allure_commons.types import AttachmentType
from pages.login_page import LoginPage


@step("the user is on the login page")
async def step_navigate(context):
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
