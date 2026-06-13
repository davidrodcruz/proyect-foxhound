import asyncio

from playwright.async_api import async_playwright


def before_all(context):
    context.shared_data = {}
    context.test_type = context.config.userdata.get("test_type")
    if context.test_type:
        context.test_type = context.test_type.strip()
    context.api_context = None
    context._playwright = None


def before_scenario(context, scenario):
    if not context.test_type:
        return

    scenario_tags = set(scenario.tags)
    if context.test_type not in scenario_tags:
        scenario.skip(f"Scenario skipped. Missing required tag: {context.test_type}")
        return

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(_setup_api_context(context))
    else:
        loop.run_until_complete(_setup_api_context(context))

    context.shared_data = {}


def after_scenario(context, scenario):
    context.shared_data = {}


async def _setup_api_context(context):
    if context.api_context:
        await context.api_context.dispose()
    context._playwright = await async_playwright().start()
    context.api_context = await context._playwright.request.new_context()


def after_all(context):
    if context.api_context:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(context.api_context.dispose())
        else:
            loop.run_until_complete(context.api_context.dispose())
    if context._playwright:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(context._playwright.stop())
        else:
            loop.run_until_complete(context._playwright.stop())
