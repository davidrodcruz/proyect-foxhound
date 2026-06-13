from behave import step
from allure import attach
from allure_commons.types import AttachmentType
from tests.api.handlers.http_handler import HttpHandler
from playwright.async_api import async_playwright


async def _ensure_api_context(context):
    if context.api_context is None:
        context._playwright = await async_playwright().start()
        context.api_context = await context._playwright.request.new_context()


@step('the "{actor}" makes a "{method}" request to "{api_host}" API to get all "{endpoint}"')
async def step_get_all(context, actor, method, api_host, endpoint):
    await _ensure_api_context(context)
    handler = HttpHandler(context.api_context)
    context.response = await handler.send_request(method, api_host, endpoint)
    attach(f"GET /posts - Status: {context.response.status}", name="Request", attachment_type=AttachmentType.TEXT)


@step('the "{actor}" makes a "{method}" request to "{api_host}" API to get "{endpoint}" with id "{item_id}"')
async def step_get_by_id(context, actor, method, api_host, endpoint, item_id):
    await _ensure_api_context(context)
    handler = HttpHandler(context.api_context)
    context.response = await handler.send_request(method, api_host, "post_by_id", id=item_id)
    attach(f"GET /posts/{item_id} - Status: {context.response.status}", name="Request", attachment_type=AttachmentType.TEXT)


@step('the "{actor}" makes a "{method}" request to "{api_host}" API to create "{endpoint}"')
async def step_prepare_create(context, actor, method, api_host, endpoint):
    await _ensure_api_context(context)
    context.api_handler = HttpHandler(context.api_context)
    context._api_host = api_host
    context._endpoint = endpoint
    attach("POST /posts - Preparing request", name="Request", attachment_type=AttachmentType.TEXT)


@step("the request body contains:")
async def step_set_body(context):
    context.request_data = {
        "title": context.table[0]["title"],
        "body": context.table[0]["body"],
        "userId": int(context.table[0]["userId"]),
    }
    context.response = await context.api_handler.send_request(
        "POST", context._api_host, context._endpoint, data=context.request_data
    )
    attach(f"POST /posts - Status: {context.response.status}", name="Request", attachment_type=AttachmentType.TEXT)


@step("the response status should be {status_code:d}")
async def step_verify_status(context, status_code):
    attach(
        f"Expected: {status_code}, Actual: {context.response.status}",
        name="Status Code",
        attachment_type=AttachmentType.TEXT,
    )
    assert context.response.status == status_code


@step("the response should contain a list of posts")
async def step_verify_list(context):
    data = await context.response.json()
    attach(f"Response body: {len(data)} posts returned", name="Response Body", attachment_type=AttachmentType.TEXT)
    assert isinstance(data, list)
    assert len(data) > 0


@step("the response should contain a post with title")
async def step_verify_post(context):
    data = await context.response.json()
    attach(f"Post title: {data.get('title', 'N/A')}", name="Response Body", attachment_type=AttachmentType.TEXT)
    assert "title" in data
