# Technical Decisions — Foxhound Test Framework

> Documento técnico que registra todas las decisiones de arquitectura, diseño y implementación del framework.

---

## 1. Stack Tecnológico

### Decisión: Python 3.11+
- **Por qué:** Mejor rendimiento (3-25% más rápido que 3.10), mejor manejo de errores con mensajes descriptivos, soporte nativo para `TaskGroup` en asyncio.
- **Alternativa descartada:** Python 3.10 (funcional pero 3.11 tiene mejoras significativas de rendimiento).

### Decisión: Playwright para UI Y API
- **Por qué:** Un solo browser driver para ambas cosas. `APIRequestContext` permite hacer peticiones HTTP sin dependencias adicionales (requests, httpx).
- **Alternativa descartada:** requests/httpx (dependencia extra, no integrado con browser context).
- **Nota:** Playwright APIRequestContext es más lento que requests puro, pero para un portafolio la simplicidad de usar una sola lib es mejor.

### Decisión: Behave como BDD runner
- **Por qué:** Requerimiento del proyecto. Gherkin nativo, steps reutilizables, `environment.py` para hooks.
- **Alternativa descartada:** pytest-bdd (más plugins pero más complejo).
- **Compensación:** Behave no tiene plugin ecosystem tan rico como pytest. Se mitiga con wrappers en `core/`.

### Decisión: Allure para reporting
- **Por qué:** Estándar industry, soporta adjuntos (screenshots, logs, curl commands), dashboard interactivo.
- **Alternativa descartada:** Reports HTML simples (menos funcional).

### Decisión: FastAPI para service-gateway
- **Por qué:** Moderno, async nativo, Swagger automático en `/docs`, type hints con Pydantic.
- **Alternativa descartada:** Flask (sync, menos features), Starlette (más bajo nivel).

---

## 2. Arquitectura de Carpetas

### Decisión: `service-gateway/` para el servidor FastAPI
- **Por qué:** Nombre descriptivo que separa claramente el "gateway" de entrada (API server) del "core" del framework.
- **Problema resuelto:** Evitar confusión entre `api/` (tests de API) y `api/` (servidor).
- **Nombre alternativo considerado:** `api-server/`, `gateway/`, `server/`.

### Decisión: `webui/teams/` para tests de UI
- **Por qué:** Consistencia con `api/teams/`. Ambos siguen la misma convención `tipo/teams/equipo/`.
- **Problema resuelto:** Antes era `teams/` solo, lo cual era inconsistente con `apis/teams/`.

### Decisión: `api/teams/` para tests de API
- **Por qué:** Separado de `service-gateway/` que es el servidor, no los tests.
- **Nota:** `api/` contiene tests de API, `service-gateway/` contiene el servidor que ejecuta tests.

### Decisión: `examples/` en vez de `templates/`
- **Por qué:** Son ejemplos con código funcional, no templates abstractos. Un desarrollador copia el ejemplo y lo modifica.
- **Nombre alternativo considerado:** `templates/`, `samples/`, `boilerplate/`.

### Decisión: `core/` como zona de contribución restringida
- **Por qué:** Evita "dependency hell". Solo mantenedores del framework modifican `core/`. Los equipos contribuyen vía PRs.
- **Regla:** `core/` NO se toca salvo cambios de arquitectura.

### Decisión: `webui/shared/` para pages compartidas
- **Por qué:** Pages como Login, Header, Footer son usadas por múltiples equipos. Van en `shared/` para evitar duplicación.

---

## 3. Patrones de Diseño

### Decisión: Page Object Model (POM) para UI
- **Por qué:** Curva de aprendizaje menor, mayor claridad para equipos heterogéneos.
- **Alternativa descartada:** Screenplay pattern (más potente pero más complejo).
- **Implementación:** Cada page tiene selectores como constantes y métodos para acciones.

### Decisión: Handler + Resources INI para API
- **Por qué:** Patrón probado en repo existente. Config centralizada de endpoints en INI.
- **Componentes:**
  - `api_resources.ini`: URLs base y endpoints mapeados
  - `http_handler.py`: Motor de peticiones con Playwright
  - `environment.py`: Setup global (before_all, shared_data)

### Decisión: `@step` genérico en vez de `@given/@when/@then`
- **Por qué:** Más flexible, un step puede ser given/when/then dependiendo del contexto.
- **Experiencia del repo anterior:** Atar steps a Given/When/Then causa duplicación cuando un step se reutiliza en diferentes contextos.

### Decisión: Allure attach en cada step
- **Por qué:** Trazabilidad completa. Cada paso genera evidencia en el reporte.
- **Patrón:**
  ```python
  from allure import attach
  from allure_commons.types import AttachmentType
  
  attach("Info relevante", name="Step Info", attachment_type=AttachmentType.TEXT)
  ```

---

## 4. Configuración

### Decisión: Config por equipo en `config.yaml`
- **Por qué:** YAML es legible por humanos y agentes. Cada equipo tiene su URL base, credenciales, flags.
- **Flujo:** `config.py` carga defaults → merge con `config.yaml` del equipo → override con env vars.

### Decisión: `api_resources.ini` para endpoints de API
- **Por qué:** Separación de concerns. Los endpoints no cambian con frecuencia, el INI es estable.
- **Formato:** INI (más simple que YAML para configuración plana de key-value).

### Decisión: `.env` para secrets
- **Por qué:** No commitear secrets. `python-dotenv` carga variables de entorno automáticamente.

---

## 5. Ejecución

### Decisión: CLI `run_tests.py` como entry point único
- **Por qué:** Un solo comando para cualquier tipo de prueba. Wrapper sobre Behave.
- **Flags:** `-t` (team), `-f` (feature), `--tags`, `-p` (parallel), `--type` (ui/api/all).

### Decisión: `subprocess.run()` para ejecutar Behave
- **Por qué:** Aísla el proceso de Behave del CLI. Manejo limpio de exit codes y output.
- **Alternativa descartada:** Llamar a Behave programáticamente (más frágil).

### Decisión: Fire & Forget para la API
- **Por qué:** La API no debe bloquearse esperando tests. Retorna 202 Accepted con run_id.
- **Flujo:** POST → genera run_id → lanza thread → retorna 202 → cliente hace polling con GET.

### Decisión: JSON para almacenamiento de runs (MVP)
- **Por qué:** Sin dependencias de base de datos. JSON en disco es suficiente para portafolio.
- **Alternativa futura:** SQLite o PostgreSQL para escala real.

---

## 6. Reporting

### Decisión: Allure con `allure_behave.formatter`
- **Por qué:** Integración nativa con Behave. Genera archivos JSON que Allure interpreta.
- **Command:** `--format allure_behave.formatter:AllureFormatter`

### Decisión: Adjuntar curl formateado en tests de API
- **Por qué:** Reproducibilidad. Si un test falla, el desarrollador puede copiar el curl y reproducir.
- **Implementación:** Genera curl string y lo adjunta con `allure.attach()`.

---

## 7. Seguridad

### Decisión: Verificación de webhook con HMAC SHA-256
- **Por qué:** Valida que el webhook viene de GitHub y no de un atacante.
- **Campo:** `X-Hub-Signature-256` en headers.
- **Secret:** `GITHUB_WEBHOOK_SECRET` desde `.env`.

---

## 8. Futuro (Iteración 2)

### MCP Self-Healing
- **Concepto:** Agente AI intercepta `ElementNotFound`, consulta DOM vía MCP, sugiere nuevo selector.
- **Hook:** `core/base_page.py` expone acciones para que MCP las use como tools.

### Base de Datos
- **Por qué:** JSON en disco no escala. SQLite para MVP, PostgreSQL para producción.

### CI/CD Pipeline
- **Por qué:** Ejecución automática en push/PR. GitHub Actions como trigger.

### Retry para Tests Flaky
- **Por qué:** Tests que fallan por timing o red. Decorator `@retry` con intentos configurables.

### Config Multi-ambiente
- **Por qué:** dev/staging/prod tienen diferentes URLs y credenciales.
- **Implementación:** `--env` flag o `config_{env}.yaml`.
