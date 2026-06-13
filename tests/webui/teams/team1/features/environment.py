import asyncio

from allure import attach
from allure_commons.types import AttachmentType


def before_all(context):
    context.shared_data = {}
    context.test_type = context.config.userdata.get("test_type")
    if context.test_type:
        context.test_type = context.test_type.strip()


def before_scenario(context, scenario):
    if not context.test_type:
        return

    scenario_tags = set(scenario.tags)
    if context.test_type not in scenario_tags:
        scenario.skip(f"Scenario skipped. Missing required tag: {context.test_type}")
        return

    context.shared_data = {}


def after_step(context, step):
    if not hasattr(context, "page") or not context.page:
        return

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_take_screenshot(context, step))
        else:
            loop.run_until_complete(_take_screenshot(context, step))
    except RuntimeError:
        asyncio.run(_take_screenshot(context, step))


async def _take_screenshot(context, step):
    try:
        screenshot = await context.page.screenshot(full_page=True)
        attach(
            screenshot,
            name=f"{step.keyword} {step.name}",
            attachment_type=AttachmentType.PNG,
        )
    except Exception:
        pass


def after_scenario(context, scenario):
    context.shared_data = {}


def after_all(context):
    async def _cleanup():
        if hasattr(context, "page") and context.page:
            await context.page.close()
        if hasattr(context, "_browser_context") and context._browser_context:
            await context._browser_context.close()
        if hasattr(context, "_browser") and context._browser:
            await context._browser.close()
        if hasattr(context, "_playwright") and context._playwright:
            await context._playwright.stop()

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_cleanup())
        else:
            loop.run_until_complete(_cleanup())
    except RuntimeError:
        asyncio.run(_cleanup())
