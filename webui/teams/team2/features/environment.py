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
