# Foxhound Steps Fix - Context Transfer

## PROJECT STRUCTURE
```
E:\Proyect-FoxHound\
├── core/
│   ├── base_page.py          # BasePage with 13 async methods (click, fill, navigate, etc.)
│   ├── api_handler.py        # Playwright APIRequestContext wrapper
│   ├── config.py             # Multi-team YAML config loader
│   └── drivers/
│       └── playwright_driver.py  # Browser/context/API factory
├── tests/
│   ├── api/
│   │   ├── handlers/
│   │   │   └── http_handler.py   # INI-based URL resolver + Playwright HTTP
│   │   ├── resources/
│   │   │   └── api_resources.ini # Endpoint URLs (jsonplaceholder, reqres)
│   │   └── teams/team1/
│   │       └── features/
│   │           ├── environment.py      # before_all, before_scenario, after_scenario, after_all
│   │           ├── posts.feature       # 3 scenarios: GET all, GET by ID, POST create
│   │           └── steps/
│   │               └── posts_steps.py  # Step definitions (uses HttpHandler)
│   ├── webui/
│   │   └── teams/team1/
│   │       └── features/
│   │           ├── environment.py      # before_all, before_scenario (test_type filtering)
│   │           ├── login.feature       # 2 scenarios: successful login, invalid login
│   │           ├── steps/
│   │           │   └── login_steps.py  # Step definitions (uses LoginPage)
│   │           └── pages/
│   │               └── login_page.py   # Page Object with selectors
│   └── examples/
│       ├── API_EXAMPLE/          # WORKING reference - uses PostsHandler
│       └── WEB_UI_EXAMPLE/       # WORKING reference - uses LoginPage
├── service-gateway/            # FastAPI server
├── run_tests.py              # CLI orchestrator: python run_tests.py -t team1 --type api
└── requirements.txt          # playwright, behave, allure-behave, fastapi, etc.
```

## HOW STEPS INTERACT

### API Tests Flow
```
posts.feature
  ↓ (behave discovers steps)
posts_steps.py
  ↓ (creates HttpHandler with context.api_context)
http_handler.py
  ↓ (reads api_resources.ini for URLs)
api_resources.ini
  ↓ (sends HTTP via Playwright)
context.response (stored for assertions)
```

### UI Tests Flow
```
login.feature
  ↓ (behave discovers steps)
login_steps.py
  ↓ (creates LoginPage with context.page)
login_page.py
  ↓ (uses Playwright Page methods)
context.page (browser state)
```

### Environment Hooks (CRITICAL)
```
tests/api/teams/team1/features/environment.py
  - before_all: context.shared_data = {}, context.test_type = userdata
  - before_scenario: skips if tag != test_type, creates Playwright APIRequestContext
  - after_scenario: clears shared_data
  - after_all: disposes api_context and playwright

tests/webui/teams/team1/features/environment.py
  - before_all: context.shared_data = {}, context.test_type = userdata
  - before_scenario: skips if tag != test_type
```

## KEY PATTERNS

### Step Definition Pattern
```python
from behave import step
from allure import attach
from allure_commons.types import AttachmentType

@step('the "{actor}" makes a "{method}" request to "{api_host}" API to get all "{endpoint}"')
async def step_get_all(context, actor, method, api_host, endpoint):
    handler = HttpHandler(context.api_context)
    context.response = await handler.send_request(method, api_host, endpoint)
    attach(f"Status: {context.response.status}", name="Request", attachment_type=AttachmentType.TEXT)
```

### Allure Attach Pattern
```python
# Always attach in every step for evidence
attach(
    f"Expected: {expected}, Actual: {actual}",
    name="Step Name",
    attachment_type=AttachmentType.TEXT
)
```

### Page Object Pattern
```python
class LoginPage:
    INPUT_USERNAME = "#user-name"
    
    def __init__(self, page: Page):
        self.page = page
    
    async def navigate(self):
        await self.page.goto("https://www.saucedemo.com/")
    
    async def login(self, username: str, password: str):
        await self.page.fill(self.INPUT_USERNAME, username)
```

## API RESOURCES INI
```ini
[api_hosts]
jsonplaceholder = https://jsonplaceholder.typicode.com
reqres = https://reqres.in/api

[api_endpoints]
posts = /posts
post_by_id = /posts/{id}
users = /users
user_by_id = /users/{id}
```

## FEATURE FILES

### posts.feature
```gherkin
Feature: Posts API on JSONPlaceholder

  @smoke @api
  Scenario: Get all posts
    Given the "user" makes a "GET" request to "jsonplaceholder" API to get all "posts"
    Then the response status should be 200
    And the response should contain a list of posts

  @api
  Scenario: Get post by ID
    Given the "user" makes a "GET" request to "jsonplaceholder" API to get "posts" with id "1"
    Then the response status should be 200
    And the response should contain a post with title

  @api
  Scenario: Create new post
    Given the "user" makes a "POST" request to "jsonplaceholder" API to create "posts"
    And the request body contains:
      | title     | body           | userId |
      | Test Post | Test content   | 1      |
    Then the response status should be 201
```

### login.feature
```gherkin
Feature: Login on SauceDemo

  Background:
    Given the user is on the login page

  @smoke @ui
  Scenario: Successful login
    When the user enters username "standard_user" and password "secret_sauce"
    And the user clicks the login button
    Then the user should see the inventory page

  @ui
  Scenario: Invalid login shows error
    When the user enters username "invalid_user" and password "wrong_password"
    And the user clicks the login button
    Then the user should see an error message "Epic sadface"
```

## COMMANDS
```bash
# Run API tests
python run_tests.py -t team1 --type api

# Run UI tests
python run_tests.py -t team1 --type ui

# Run specific feature
python run_tests.py -t team1 --type api -f posts.feature

# Run with tags
python run_tests.py -t team1 --type api --tags @smoke
```

## EXAMPLES (WORKING REFERENCES)
- `tests/examples/API_EXAMPLE/` - Uses PostsHandler (simpler than HttpHandler)
- `tests/examples/WEB_UI_EXAMPLE/` - Uses LoginPage directly

## COMMON ISSUES TO CHECK
1. Steps not matching feature file text (spacing, quotes, punctuation)
2. Missing `@step` decorator (must use `@step` not `@given/@when/@then`)
3. Async steps must be `async def` and use `await`
4. `context.api_context` must exist (created in environment.py before_scenario)
5. `context.page` must exist for UI tests (created by behave-playwright or environment.py)
6. INI endpoint names must match what's in feature file (e.g., "posts" not "post_by_id")
7. Allure attach must use `AttachmentType.TEXT` not string
8. Steps must import from correct paths (relative imports may fail)
