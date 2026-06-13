from behave import step
from allure import attach
from allure_commons.types import AttachmentType
from tests.examples.API_EXAMPLE.handlers.posts_handler import PostsHandler


@step('the "{actor}" makes a "{method}" request to "{api_host}" API to get all "{endpoint}"')
async def step_get_all(context, actor, method, api_host, endpoint):
    handler = PostsHandler(context.api_context)
    context.response = await handler.get_all_posts()
    attach(f"GET /posts - Status: {context.response.status}", name="Request", attachment_type=AttachmentType.TEXT)


@step('the "{actor}" makes a "{method}" request to "{api_host}" API to get "{endpoint}" with id "{item_id}"')
async def step_get_by_id(context, actor, method, api_host, endpoint, item_id):
    handler = PostsHandler(context.api_context)
    context.response = await handler.get_post_by_id(int(item_id))
    attach(f"GET /posts/{item_id} - Status: {context.response.status}", name="Request", attachment_type=AttachmentType.TEXT)


@step('the "{actor}" makes a "{method}" request to "{api_host}" API to create "{endpoint}"')
async def step_prepare_create(context, actor, method, api_host, endpoint):
    context.api_handler = PostsHandler(context.api_context)
    attach("POST /posts - Preparing request", name="Request", attachment_type=AttachmentType.TEXT)


@step("the request body contains:")
async def step_set_body(context):
    context.request_data = {
        "title": context.table[0]["title"],
        "body": context.table[0]["body"],
        "userId": int(context.table[0]["userId"]),
    }
    context.response = await context.api_handler.create_post(context.request_data)
    attach(f"POST /posts - Status: {context.response.status}", name="Request", attachment_type=AttachmentType.TEXT)


@step("the response status should be {status_code:d}")
def step_verify_status(context, status_code):
    attach(
        f"Expected: {status_code}, Actual: {context.response.status}",
        name="Status Code",
        attachment_type=AttachmentType.TEXT,
    )
    assert context.response.status == status_code


@step("the response should contain a list of posts")
def step_verify_list(context):
    data = context.response.json()
    attach(f"Response body: {len(data)} posts returned", name="Response Body", attachment_type=AttachmentType.TEXT)
    assert isinstance(data, list)
    assert len(data) > 0


@step("the response should contain a post with title")
def step_verify_post(context):
    data = context.response.json()
    attach(f"Post title: {data.get('title', 'N/A')}", name="Response Body", attachment_type=AttachmentType.TEXT)
    assert "title" in data
