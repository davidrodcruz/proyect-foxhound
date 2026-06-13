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

    context.shared_data = {}


def after_scenario(context, scenario):
    context.shared_data = {}


def after_all(context):
    import asyncio

    async def _cleanup():
        if context.api_context:
            await context.api_context.dispose()
        if context._playwright:
            await context._playwright.stop()

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_cleanup())
        else:
            loop.run_until_complete(_cleanup())
    except RuntimeError:
        asyncio.run(_cleanup())
