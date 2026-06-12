# Foxhound Test Framework

> Framework de automatización de pruebas BDD (Web UI + API) para portafolio personal.
> Playwright + Python + Behave + Allure + FastAPI

---

## Overview

Foxhound es un framework que demuestra dominio de automatización de pruebas con tecnologías modernas. Soporta pruebas de Web UI y API con una estructura escalable por equipos, incluyendo una capa API para ejecutar tests vía HTTP y recibir webhooks de GitHub Actions.

---

## Stack

| Tecnología | Uso |
|------------|-----|
| **Python 3.11+** | Lenguaje principal |
| **Playwright** | Browser automation + API testing |
| **Behave** | BDD runner (Gherkin) |
| **Allure** | Reporting y evidencia |
| **FastAPI** | REST API + webhooks |
| **Uvicorn** | ASGI server |

---

## Estructura del Proyecto

```
.
├── service-gateway/        # FastAPI Server (API-first)
├── core/                   # Framework engine (clases base)
├── webui/teams/            # Web UI tests por equipo
├── api/teams/              # API tests por equipo
├── examples/               # Ejemplos documentados
├── results/                # Artifacts de ejecución
├── run_tests.py            # CLI entry point
├── Dockerfile              # Imagen Docker
├── docker-compose.yml      # Server en Docker
├── docker-compose.test.yml # Tests en Docker
└── requirements.txt
```

---

## Inicio Rápido

### 1. Instalar dependencias

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
playwright install
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 3. Ejecutar tests

```bash
# CLI: Ejecutar tests de un equipo
python run_tests.py -t team1 --type api

# CLI: Ejecutar un feature específico
python run_tests.py -t team1 --type api -f posts.feature

# CLI: Ejecutar por tag
python run_tests.py -t team1 --tags @smoke
```

### 4. Ejecutar vía API

```bash
# Levantar servidor
uvicorn service-gateway.server:app --reload --port 8000

# Ejecutar tests
curl -X POST http://localhost:8000/api/v1/tests/run \
  -H "Content-Type: application/json" \
  -d '{"team": "team1", "type": "api", "feature": "posts.feature", "tags": "@smoke"}'

# Consultar estado
curl http://localhost:8000/api/v1/tests/run/{run_id}

# Swagger docs
open http://localhost:8000/docs
```

---

## Docker

### Qué es cada archivo

| Archivo | Propósito |
|---------|-----------|
| `Dockerfile` | Define la imagen: Python 3.11 + Java (Allure) + Playwright + dependencias del sistema |
| `.dockerignore` | Exclude archivos innecesarios del build (.git, plans, results, docs) |
| `docker-compose.yml` | Levanta el server FastAPI en puerto 8000 |
| `docker-compose.test.yml` | Ejecuta tests via CLI sin levantar server |

### Build de la imagen

```bash
# Construir imagen Docker (una sola vez, o después de cambiar dependencias)
docker compose build
```

### Ejecutar el server en Docker

```bash
# Levantar server FastAPI en background
docker compose up -d

# Ver logs del server en tiempo real
docker compose logs -f

# Detener server
docker compose down
```

### Ejecutar tests en Docker

```bash
# Ejecutar tests de un equipo (API)
docker compose -f docker-compose.test.yml run --rm tests \
  python run_tests.py -t team1 --type api

# Ejecutar tests de un equipo (UI)
docker compose -f docker-compose.test.yml run --rm tests \
  python run_tests.py -t team1 --type ui

# Ejecutar un feature específico
docker compose -f docker-compose.test.yml run --rm tests \
  python run_tests.py -t team1 --type api -f posts.feature

# Ejecutar por tag
docker compose -f docker-compose.test.yml run --rm tests \
  python run_tests.py -t team1 --tags @smoke

# Ejecutar todo (UI + API)
docker compose -f docker-compose.test.yml run --rm tests \
  python run_tests.py -t team1 --type all
```

### Ver resultados

```bash
# Los resultados se guardan en ./results/ (montado como volumen)
ls results/

# Abrir reporte Allure (requiere Allure CLI instalado localmente)
allure serve results/allure-results
```

---

## CLI Reference

| Flag | Descripción | Ejemplo |
|------|-------------|---------|
| `-t`, `--team` | Equipo a ejecutar | `--team team1` |
| `-f`, `--feature` | Feature file específico | `--feature login.feature` |
| `--tags` | Filtrar por tags Behave | `--tags @smoke` |
| `-p`, `--parallel` | Ejecución paralela | `--parallel 2` |
| `--type` | Tipo: `ui`, `api` o `all` | `--type api` |

---

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/tests/run` | Ejecutar tests (fire & forget) |
| `GET` | `/api/v1/tests/run/{run_id}` | Consultar estado |
| `GET` | `/api/v1/tests/run/{run_id}/report` | Descargar reporte Allure |
| `POST` | `/api/v1/webhooks/github` | Webhook GitHub Actions |
| `GET` | `/api/v1/health` | Health check |

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

## Ejemplos

### Web UI: Login en SauceDemo
- Site: `https://www.saucedemo.com/`
- Features: Login exitoso, login inválido
- Patrón: Page Object Model

### API: Posts CRUD en JSONPlaceholder
- API: `https://jsonplaceholder.typicode.com`
- Features: GET all, GET by ID, POST create
- Patrón: Handler + Resources INI

Ver `examples/` para código completo.

---

## Documentación

- [Technical Decisions](docs/technical-decisions.md) — Todas las decisiones de arquitectura
- [Plan del Proyecto](.plans/foxhound-test-framework.md) — Plan completo de implementación

---

## Futuro

- POST resultado de vuelta al webhook de GitHub
- Base de datos (SQLite/PostgreSQL)
- Autenticación JWT
- Dashboard web
- MCP self-healing con AI agent
- CI/CD pipeline
- Config multi-ambiente (dev/staging/prod)

---

## Autor

**Davo** — Software Engineer in Test

---

## Licencia

MIT
