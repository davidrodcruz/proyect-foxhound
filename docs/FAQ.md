# FAQ - Foxhound Test Framework

## Comandos de Ejemplo para Ejecución de Pruebas

### Ejecución vía CLI (Local)
Utiliza `run_tests.py` como punto de entrada único para cualquier tipo de prueba.

| Objetivo | Comando |
|----------|---------|
| Ejecutar tests API de un equipo | `python run_tests.py -t team1 --type api` |
| Ejecutar tests UI de un equipo | `python run_tests.py -t team1 --type ui` |
| Ejecutar todas las pruebas (UI + API) de un equipo | `python run_tests.py -t team1 --type all` |
| Ejecutar un feature file específico (busca en UI y API) | `python run_tests.py -t team1 -f posts.feature` |
| Ejecutar un feature file específico (solo API) | `python run_tests.py -t team1 --type api -f posts.feature` |
| Ejecutar pruebas filtradas por tags | `python run_tests.py -t team1 --tags @smoke` |

### Ejecución en Docker
Usa el archivo `docker-compose.test.yml` para ejecutar los tests aislados sin levantar el servidor FastAPI.

| Objetivo | Comando |
|----------|---------|
| Ejecutar tests de UI de un equipo | `docker compose -f docker-compose.test.yml run --rm tests python run_tests.py -t team1 --type ui` |
| Ejecutar tests de API de un equipo | `docker compose -f docker-compose.test.yml run --rm tests python run_tests.py -t team1 --type api` |
| Ejecutar un feature específico en Docker | `docker compose -f docker-compose.test.yml run --rm tests python run_tests.py -t team1 --type api -f posts.feature` |

### Ejecución vía API (Gateway)
El servidor FastAPI permite disparar pruebas de forma asíncrona ("fire & forget").

**Levantar el servidor:**
`uvicorn service-gateway.server:app --reload --port 8000`

**Disparar ejecución de tests:**
```bash
curl -X POST http://localhost:8000/api/v1/tests/run \
  -H "Content-Type: application/json" \
  -d '{"team": "team1", "type": "api", "feature": "posts.feature", "tags": "@smoke"}'
```

**Consultar estado y reporte:**
- Estado: `GET http://localhost:8000/api/v1/tests/run/{run_id}`
- Reporte Allure: `GET http://localhost:8000/api/v1/tests/run/{run_id}/report`

## Entradas y Salidas Esperadas (Entry Points & Outputs)

### Entry Points Principales
- `run_tests.py`: CLI principal, acepta flags `-t`, `-f`, `--tags`, `-p`, `--type`.
- `service-gateway/server:app`: API para gestión de ejecuciones.
- `webhooks/github`: Endpoint para recibir notificaciones y disparar procesos.

### Outputs Generados
- **Consola:** Logs en tiempo real de la ejecución de Behave y el procesamiento del CLI.
- **Archivos de Resultado:** Directorio `./results/` que contiene los artefactos ejecutables.
- **Reportes:** `allure-results` generados dentro de la carpeta de resultados, compatibles con Allure CLI para visualización interactiva (`allure serve results/allure-results`).
- **API Responses:** 
  - `202 Accepted`: Para solicitudes POST exitosas al disparar tests.
  - JSON: Datos de estado y progreso del run_id.

## Convenciones de Tags
- `@smoke`: Pruebas críticas rápidas (Happy path).
- `@regression`: Suite completa de pruebas.
- `@wip`: Pruebas en desarrollo.
- `@api` / `@ui`: Identificadores de tipo de prueba.
- `@critical`: Pruebas bloqueantes.

## Errores Comunes y Soluciones

### `AttributeError` / `NoneType` en `context.api_context` durante steps API

**Causa:** Los hooks de Behave (`before_scenario`, `after_all`) son funciones síncronas. Si intentan ejecutar código async de Playwright con `asyncio.get_event_loop().run_until_complete()`, fallan silenciosamente porque behave ya tiene un event loop corriendo para los steps async. El `context.api_context` queda como `None`.

**Solución:** Usar lazy-init dentro de los step definitions. Cada step que necesita `api_context` debe llamar a `_ensure_api_context(context)` antes de usarlo:

```python
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
```

**Por qué funciona:** Los steps async de Behave se ejecutan dentro de un event loop. Crear el `APIRequestContext` dentro del step garantiza que se usa el mismo loop que Behave.

**Regla:** Cuando crees nuevos steps API async, siempre incluye `_ensure_api_context` al inicio.

### `TypeError` / `AttributeError` al llamar `.json()` en steps de verificación

**Causa:** Los steps de verificación (`step_verify_list`, `step_verify_status`, `step_verify_post`) eran síncronos (`def`), pero `context.response` viene de `async_playwright`, donde `.json()` es un método async. Sin `await`, `data` queda como corrutina no resuelta.

**Solución:** Los steps que acceden a `context.response.json()` deben ser `async def` y usar `await`:

```python
# ❌ Incorrecto - .json() es async pero el step es sync
@step("the response should contain a list of posts")
def step_verify_list(context):
    data = context.response.json()  # data es una corrutina, no una lista

# ✅ Correcto
@step("the response should contain a list of posts")
async def step_verify_list(context):
    data = await context.response.json()
```

**Regla:** Cada step que acceda a `context.response.json()` debe ser `async def` con `await`.

### `ModuleNotFoundError: No module named 'pages'` en steps UI

**Causa:** La estructura de directorios del equipo tiene `pages/` fuera de `features/`:
```
tests/webui/teams/team1/
├── features/
│   └── steps/
│       └── login_steps.py    # importa "from tests.webui.teams.team1.pages.login_page"
└── pages/
    └── login_page.py         # está un nivel arriba
```
Python no encuentra `pages` porque solo busca en el directorio actual y `sys.path`.

**Solución:** Agregar el directorio raíz del equipo al `sys.path` al inicio del step file:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pages.login_page import LoginPage
```

**Regla:** Cuando crees nuevos page objects en `teams/<team>/pages/`, usa este patrón de import en los steps.

### `AttributeError` en `context.page` durante steps UI

**Causa:** El `environment.py` de UI no crea el browser de Playwright. Los hooks son síncronos y no pueden inicializar objetos async.

**Solución:** Lazy-init del browser en el step que primero necesite `context.page`:

```python
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
```

**Regla:** El primer step UI de cada scenario debe llamar `await _ensure_page(context)`.
