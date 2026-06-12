# FAQ - Foxhound Test Framework

## Comandos de Ejemplo para Ejecución de Pruebas

### Ejecución vía CLI (Local)
Utiliza `run_tests.py` como punto de entrada único para cualquier tipo de prueba.

| Objetivo | Comando |
|----------|---------|
| Ejecutar tests de un equipo específico (API) | `python run_tests.py -t team1 --type api` |
| Ejecutar un feature file específico | `python run_tests.py -t team1 --type api -f posts.feature` |
| Ejecutar pruebas filtradas por tags | `python run_tests.py -t team1 --tags @smoke` |
| Ejecutar todas las pruebas (UI + API) de un equipo | `python run_tests.py -t team1 --type all` |

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
