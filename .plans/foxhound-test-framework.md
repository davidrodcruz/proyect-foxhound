# Foxhound Test Framework — MVP

> Framework de automatización de pruebas (Web UI + API) para portafolio personal.
> Playwright + Python + Behave + Allure + FastAPI

---

## Overview

Foxhound es un framework BDD para automatización de pruebas que demuestra dominio de Playwright, Behave, patrones de diseño como POM, y generación de reportes con Allure. Soporta pruebas de Web UI y API con una estructura escalable por equipos. Incluye una capa FastAPI (`service_gateway/`) para ejecutar tests vía REST API y recibir webhooks de GitHub Actions.

---

## Goals

1. CLI único (`run_tests.py`) para ejecutar cualquier prueba (UI o API)
2. API REST (`service_gateway/`) para ejecutar tests vía HTTP
3. Webhook endpoint para GitHub Actions
4. Soporte Web UI y API usando Playwright para ambos
5. Estructura `webui/teams/` para UI y `api/teams/` para API
6. 2 ejemplos documentados para crear más tests
7. Reportes Allure
8. Preparado para MCP (self-healing) en futuro

---

## Stack

- **Python 3.11+** (mejor rendimiento, mejor manejo de errores)
- **Playwright** (browser + API testing con APIRequestContext)
- **Behave** (BDD runner)
- **Allure** (reporting)
- **FastAPI** (REST API + webhooks)
- **Uvicorn** (ASGI server)

---

## Folder Structure

```text
.
├── service_gateway/                    # 🔌 FastAPI Server (API-first entry point)
│   ├── __init__.py
│   ├── server.py                       # FastAPI app principal + startup/shutdown
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── tests.py                    # POST /api/v1/tests/run, GET /api/v1/tests/run/{id}
│   │   └── webhooks.py                # POST /api/v1/webhooks/github
│   ├── models/
│   │   ├── __init__.py
│   │   └── test_run.py                # Pydantic models (request/response)
│   ├── services/
│   │   ├── __init__.py
│   │   └── test_runner.py             # Ejecuta tests en background (threading)
│   └── store/
│       ├── __init__.py
│       └── run_history.py             # Estado de ejecuciones (JSON en disco)
│
├── core/                               # Framework engine (clases base)
│   ├── __init__.py
│   ├── base_page.py                    # Page Object base (UI)
│   ├── api_handler.py                  # Handler HTTP usando Playwright APIRequestContext
│   ├── config.py                       # Carga config por equipo
│   └── drivers/
│       ├── __init__.py
│       └── playwright_driver.py        # Factory browser/context + APIRequestContext
│
├── webui/                              # 🌐 Web UI tests por equipo
│   ├── teams/
│   │   ├── team1/
│   │   │   ├── features/
│   │   │   │   ├── login.feature
│   │   │   │   └── steps/
│   │   │   │       └── login_steps.py
│   │   │   └── pages/
│   │   │       └── login_page.py
│   │   └── team2/
│   │       ├── features/
│   │       │   ├── dashboard.feature
│   │       │   └── steps/
│   │       │       └── dashboard_steps.py
│   │       └── pages/
│   │           └── dashboard_page.py
│   └── shared/                         # Pages compartidas entre equipos UI
│       ├── __init__.py
│       ├── login_page.py
│       ├── header_page.py
│       └── footer_page.py
│
├── api/                                # 🔌 API tests por equipo
│   ├── environment.py                  # Setup global API (before_all, shared_data)
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── http_handler.py            # Motor de peticiones HTTP con Playwright
│   ├── resources/
│   │   └── api_resources.ini          # URLs base y endpoints mapeados
│   └── teams/
│       ├── team1/
│       │   ├── features/
│       │   │   ├── posts.feature
│       │   │   └── steps/
│       │   │       └── posts_steps.py
│       │   └── config.yaml
│       └── team2/
│           ├── features/
│           │   ├── users.feature
│           │   └── steps/
│           │       └── users_steps.py
│           └── config.yaml
│
├── examples/                           # 📋 Ejemplos documentados
│   ├── WEB_UI_EXAMPLE/
│   │   ├── README.md                   # Cómo usar este ejemplo como base
│   │   ├── login.feature               # Feature: Login en SauceDemo
│   │   ├── steps/
│   │   │   ├── __init__.py
│   │   │   └── login_steps.py          # Step definitions
│   │   └── pages/
│   │       ├── __init__.py
│   │       └── login_page.py           # Page Object: LoginPage
│   └── API_EXAMPLE/
│       ├── README.md                   # Cómo usar este ejemplo como base
│       ├── posts.feature               # Feature: CRUD Posts en JSONPlaceholder
│       ├── steps/
│       │   ├── __init__.py
│       │   └── posts_steps.py          # Step definitions
│       └── handlers/
│           ├── __init__.py
│           └── posts_handler.py        # Handler wrapper
│
├── results/                            # 📊 Artifacts de ejecución
│   ├── {run_id}/                       # Por cada ejecución vía API
│   │   ├── allure-results/
│   │   └── status.json
│   └── runs.json                       # Historial de ejecuciones
│
├── run_tests.py                        # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## Ejemplos Detallados

### Ejemplo Web UI: Login en SauceDemo

**Site:** `https://www.saucedemo.com/` (demo público de Sauce Labs)

**`examples/WEB_UI_EXAMPLE/login.feature`:**
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

**`examples/WEB_UI_EXAMPLE/pages/login_page.py`:**
```python
class LoginPage:
    # Selectors
    INPUT_USERNAME = "#user-name"
    INPUT_PASSWORD = "#password"
    BTN_LOGIN = "#login-button"
    ERROR_MESSAGE = "[data-test='error']"

    def __init__(self, page):
        self.page = page

    async def navigate(self):
        await self.page.goto("https://www.saucedemo.com/")

    async def login(self, username: str, password: str):
        await self.page.fill(self.INPUT_USERNAME, username)
        await self.page.fill(self.INPUT_PASSWORD, password)
        await self.page.click(self.BTN_LOGIN)

    async def get_error_message(self) -> str:
        return await self.page.text_content(self.ERROR_MESSAGE)
```

**`examples/WEB_UI_EXAMPLE/steps/login_steps.py`:**
```python
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
```

---

### Ejemplo API: Posts CRUD en JSONPlaceholder

**API:** `https://jsonplaceholder.typicode.com`

**`examples/API_EXAMPLE/posts.feature`:**
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

**`examples/API_EXAMPLE/handlers/posts_handler.py`:**
```python
from core.api_handler import ApiHandler

class PostsHandler:
    def __init__(self):
        self.api = ApiHandler()
        self.host = "jsonplaceholder"

    async def get_all_posts(self):
        return await self.api.get(self.host, "posts")

    async def get_post_by_id(self, post_id: int):
        return await self.api.get(self.host, f"posts/{post_id}")

    async def create_post(self, data: dict):
        return await self.api.post(self.host, "posts", data=data)
```

**`examples/API_EXAMPLE/steps/posts_steps.py`:**
```python
from behave import step
from allure import attach
from allure_commons.types import AttachmentType
from handlers.posts_handler import PostsHandler

@step('the "{actor}" makes a "{method}" request to "{api_host}" API to get all "{endpoint}"')
async def step_get_all(context, actor, method, api_host, endpoint):
    handler = PostsHandler()
    context.response = await handler.get_all_posts()
    attach(f"GET /posts - Status: {context.response.status}", name="Request", attachment_type=AttachmentType.TEXT)

@step('the "{actor}" makes a "{method}" request to "{api_host}" API to get "{endpoint}" with id "{item_id}"')
async def step_get_by_id(context, actor, method, api_host, endpoint, item_id):
    handler = PostsHandler()
    context.response = await handler.get_post_by_id(int(item_id))
    attach(f"GET /posts/{item_id} - Status: {context.response.status}", name="Request", attachment_type=AttachmentType.TEXT)

@step('the "{actor}" makes a "{method}" request to "{api_host}" API to create "{endpoint}"')
async def step_prepare_create(context, actor, method, api_host, endpoint):
    context.api_handler = PostsHandler()
    attach(f"POST /posts - Preparing request", name="Request", attachment_type=AttachmentType.TEXT)

@step("the request body contains:")
async def step_set_body(context):
    context.request_data = {
        "title": context.table[0]["title"],
        "body": context.table[0]["body"],
        "userId": int(context.table[0]["userId"])
    }
    context.response = await context.api_handler.create_post(context.request_data)
    attach(f"POST /posts - Status: {context.response.status}", name="Request", attachment_type=AttachmentType.TEXT)

@step("the response status should be {status_code:d}")
def step_verify_status(context, status_code):
    attach(f"Expected: {status_code}, Actual: {context.response.status}", name="Status Code", attachment_type=AttachmentType.TEXT)
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
```

---

**Por qué estos ejemplos:**

| Criterio | Web UI (SauceDemo) | API (JSONPlaceholder) |
|----------|--------------------|-----------------------|
| Público | ✅ Sin login previo | ✅ Sin auth |
| Conocido | ✅ Estándar industry | ✅ Muy usado en tutoriales |
| CRUD completo | ✅ Login → Dashboard | ✅ GET/POST/PUT/DELETE |
| Demuestra patrones | ✅ POM, steps, assertions | ✅ Handler, INI, shared_data |
| Portafolio | ✅ Reclutador lo reconoce | ✅ Demuestra API testing |

---

## API Pattern: Handlers + Resources INI

Patrón heredado de tu repo existente, adaptado para usar Playwright en vez de requests.

### `api/resources/api_resources.ini`
```ini
[api_hosts]
jsonplaceholder = https://jsonplaceholder.typicode.com
reqres = https://reqres.in/api

[api_endpoints]
posts = /posts
post_by_id = /posts/{id}
users = /users
user_by_id = /users/{id}
comments = /posts/{id}/comments
```

### `api/handlers/http_handler.py`
```python
# Funciones principales:
# - get_url_property(section, key) → lee de api_resources.ini
# - construct_url(host, endpoint, params) → reemplaza {id}, etc.
# - send_request(method, api_host, endpoint, data, headers) → ejecuta con Playwright
#   - Usa APIRequestContext de Playwright (NO requests)
#   - Genera curl formateado para Allure attach
#   - Maneja respuestas vacías con respuesta sintética
```

### `api/environment.py`
```python
# before_all(context):
#   - Inicializa Playwright APIRequestContext
#   - Crea context.shared_data = {}
#   - Carga config del equipo
#
# after_all(context):
#   - Cierra APIRequestContext
#
# before_scenario(context, scenario):
#   - Filtra por tag @api
#   - Limpia shared_data entre escenarios
```

### Flujo de una prueba API
```
1. Feature: posts.feature
   Scenario: Get all posts
     Given the "user" makes a "GET" request to "jsonplaceholder" API to get all "posts"

2. Step definitions (posts_steps.py):
   - Captura: actor="user", method="GET", api_host="jsonplaceholder", endpoint="posts"
   - Llama a http_handler.send_request("GET", "jsonplaceholder", "posts")
   - Guarda respuesta en context.shared_data["response"]

3. Handler (http_handler.py):
   - get_url_property("api_hosts", "jsonplaceholder") → "https://jsonplaceholder.typicode.com"
   - get_url_property("api_endpoints", "posts") → "/posts"
   - construct_url(host, endpoint) → "https://jsonplaceholder.typicode.com/posts"
   - Playwright APIRequestContext.request("GET", url)
   - Allure.attach(curl_command)
   - Retorna response

4. Validación en steps:
   - assert response.status == 200
   - assert len(response.json()) > 0
```

---

## FastAPI Server: `service_gateway/`

### Endpoints

| Método | Ruta | Descripción | Body/Params |
|--------|------|-------------|-------------|
| `POST` | `/api/v1/tests/run` | Ejecutar tests (fire & forget) | `{ "team": "team1", "type": "api", "feature": "posts.feature", "tags": "@smoke" }` |
| `GET` | `/api/v1/tests/run/{run_id}` | Consultar estado de ejecución | — |
| `GET` | `/api/v1/tests/run/{run_id}/report` | Descargar reporte Allure (ZIP) | — |
| `POST` | `/api/v1/webhooks/github` | Recibir webhook de GitHub Actions | Payload GitHub |
| `GET` | `/api/v1/health` | Health check | — |

### `service_gateway/server.py`
```python
# FastAPI app con:
# - CORS habilitado
# - Lifespan handler (startup: crea results/, shutdown: cleanup)
# - Incluye todos los routers (tests, webhooks)
# - Swagger automático en /docs
```

### `service_gateway/routes/tests.py`
```python
# POST /api/v1/tests/run:
#   - Valida request con Pydantic model
#   - Genera run_id (UUID)
#   - Guarda estado "pending" en run_history
#   - Lanza thread con test_runner.execute()
#   - Retorna 202 Accepted con run_id
#
# GET /api/v1/tests/run/{run_id}:
#   - Busca run_id en run_history
#   - Retorna status, timestamps, exit_code
#
# GET /api/v1/tests/run/{run_id}/report:
#   - Verifica que status = completed
#   - Empaqueta results/{run_id}/allure-results/ en ZIP
#   - Retorna archivo ZIP
```

### `service_gateway/routes/webhooks.py`
```python
# POST /api/v1/webhooks/github:
#   - Verifica X-Hub-Signature-256 (HMAC SHA-256)
#   - Extrae info del payload (repo, branch, commit, action)
#   - Crea test run con contexto del webhook
#   - Ejecuta tests en background
#   - Retorna 202 Accepted con run_id
#
# Secret: GITHUB_WEBHOOK_SECRET desde .env
```

### `service_gateway/services/test_runner.py`
```python
# execute(run_id, config):
#   - Actualiza status a "running"
#   - Construye comando: python run_tests.py -t {team} --type {type} -f {feature} --tags {tags}
#   - Ejecuta con subprocess.run()
#   - Guarda stdout/stderr en results/{run_id}/output.log
#   - Actualiza status a "completed" o "failed" según exit_code
#   - En thread separado para no bloquear
```

### `service_gateway/store/run_history.py`
```python
# Almacena en memoria + archivo results/runs.json
# Estructura por run:
#   - run_id: str (UUID)
#   - status: "pending" | "running" | "completed" | "failed"
#   - team: str
#   - type: "ui" | "api" | "all"
#   - feature: str | None
#   - tags: str | None
#   - created_at: datetime
#   - started_at: datetime | None
#   - finished_at: datetime | None
#   - exit_code: int | None
#   - github_payload: dict | None (si viene de webhook)
```

### Ejemplos de uso API

```bash
# Levantar el servidor
uvicorn service_gateway.server:app --reload --port 8000

# Ejecutar tests vía API
curl -X POST http://localhost:8000/api/v1/tests/run \
  -H "Content-Type: application/json" \
  -d '{"team": "team1", "type": "api", "feature": "posts.feature", "tags": "@smoke"}'

# Respuesta:
# { "run_id": "abc-123", "status": "pending", "message": "Tests en cola de ejecución" }

# Consultar estado
curl http://localhost:8000/api/v1/tests/run/abc-123

# Descargar reporte
curl http://localhost:8000/api/v1/tests/run/abc-123/report -o report.zip

# Swagger docs
open http://localhost:8000/docs
```

---

## CLI Orchestrator: `run_tests.py`

### Flags soportados

| Flag | Descripción | Ejemplo |
|------|-------------|---------|
| `-t`, `--team` | Equipo a ejecutar | `--team team1` |
| `-f`, `--feature` | Feature file específico | `--feature login.feature` |
| `--tags` | Filtrar por tags Behave | `--tags @smoke` |
| `-p`, `--parallel` | Ejecución paralela (N procesos) | `--parallel 2` |
| `--type` | Tipo de prueba: `ui`, `api` o `all` | `--type api` |

### Ejemplos de uso

```bash
# Ejecutar UI tests de un equipo
python run_tests.py -t team1 --type ui

# Ejecutar API tests de un equipo
python run_tests.py -t team1 --type api

# Ejecutar todo de un equipo (UI + API)
python run_tests.py -t team1 --type all

# Ejecutar un feature específico de API
python run_tests.py -t team1 --type api -f posts.feature

# Ejecutar por tag
python run_tests.py -t team1 --tags @smoke

# Ejecutar 2 equipos en paralelo
python run_tests.py -t team1,team2 -p 2
```

### Flujo interno

```
1. Parsear args CLI
2. Determinar tipo (ui/api/all)
3. Si tipo = ui o all:
   - Cargar webui/teams/{team}/config.yaml
   - Descubrir features en webui/teams/{team}/features/
4. Si tipo = api o all:
   - Cargar api/teams/{team}/config.yaml
   - Cargar api/resources/api_resources.ini
   - Descubrir features en api/teams/{team}/features/
5. Construir comando behave con:
   --format allure_behave.formatter:AllureFormatter
   --outfile=results/allure-results
   --tags=<filtro>
   <paths de features>
6. Ejecutar behave
7. Return exit code
```

---

## Componentes Core

### `core/base_page.py`
Métodos: `navigate()`, `click()`, `fill()`, `wait_for()`, `get_text()`, `is_visible()`, `screenshot()`

### `core/api_handler.py`
Wrapper sobre Playwright `APIRequestContext`:
- `get()`, `post()`, `put()`, `delete()`
- Logging de request/response
- Genera curl formateado para Allure
- Timeout configurable

### `core/config.py`
Carga config desde `webui/teams/{team}/config.yaml` o `api/teams/{team}/config.yaml` + env vars

### `core/drivers/playwright_driver.py`
- `create_browser()` → browser + context para UI
- `create_api_context()` → APIRequestContext para APIs

---

## Tag Convention

| Tag | Uso |
|-----|-----|
| `@smoke` | Happy path, rápido |
| `@regression` | Suite completa |
| `@wip` | En desarrollo |
| `@api` | Prueba de API |
| `@ui` | Prueba de Web UI |
| `@critical` | Bloqueante |

---

## Execution Plan

### Fase 1: Core + CLI (3-4 días)
1. Crear estructura de carpetas con `__init__.py`
2. Implementar `core/config.py`
3. Implementar `core/base_page.py`
4. Implementar `core/api_handler.py` (Playwright APIRequestContext)
5. Implementar `core/drivers/playwright_driver.py`
6. Implementar `api/handlers/http_handler.py`
7. Implementar `api/environment.py`
8. Implementar `api/resources/api_resources.ini`
9. Implementar `run_tests.py` con `-t`, `-f`, `--tags`, `--type`
10. Configurar Allure

### Fase 2: Ejemplos (2-3 días)
1. Ejemplo Web UI: feature + steps + page object
2. Ejemplo API: feature + steps + handler + INI
3. Documentar ambos ejemplos

### Fase 3: Ejemplos en teams (2-3 días)
1. Crear `webui/teams/team1/` con pruebas UI (ej: login)
2. Crear `api/teams/team1/` con pruebas API (ej: JSONPlaceholder posts)
3. Probar CLI completo end-to-end

### Fase 4: FastAPI Server + Webhooks (2-3 días)
1. Implementar `service_gateway/server.py` (FastAPI app)
2. Implementar `service_gateway/models/test_run.py` (Pydantic models)
3. Implementar `service_gateway/store/run_history.py` (JSON storage)
4. Implementar `service_gateway/services/test_runner.py` (background execution)
5. Implementar `service_gateway/routes/tests.py` (POST run, GET status, GET report)
6. Implementar `service_gateway/routes/webhooks.py` (GitHub webhook)
7. Agregar `GITHUB_WEBHOOK_SECRET` a `.env.example`
8. Probar endpoints con curl/Postman

### Fase 5: MCP Prep (1 día)
1. Agregar hooks en `core/base_page.py` para logging de acciones
2. Documentar puntos de integración futura con MCP

---

## Success Criteria

1. `python run_tests.py -t team1 --type api -f posts.feature` ejecuta y genera reporte Allure
2. `curl -X POST localhost:8000/api/v1/tests/run ...` ejecuta tests vía API
3. GitHub webhook recibe payload y ejecuta tests en background
4. Ejemplos documentados permiten crear un nuevo test en <30 min
5. Estructura `webui/teams/` y `api/teams/` permite agregar equipos nuevos copiando y modificando
6. Código limpio, type hints, sin errores de linting

---

## Futuro (iteración 2)

- POST resultado de vuelta al webhook de GitHub
- Base de datos (SQLite/PostgreSQL) en vez de JSON
- Autenticación JWT para la API
- Dashboard web para ver historial
- Paralelismo real con multiprocessing
- Screenshots automáticos en failure
- Retry para tests flaky
- MCP self-healing con AI agent
- Config multi-ambiente (dev/staging/prod)
