# Docker & API Execution Guide

> Guía completa para ejecutar tests usando Docker y la API REST.

---

## 1. Prerrequisitos

| Requisito | Versión mínima |
|-----------|----------------|
| Docker | 20.10+ |
| Docker Compose | 2.0+ |

---

## 2. Construir la imagen Docker

```bash
# Desde la raíz del proyecto
<docker compose build>
```

Esto genera una imagen con:
- Python 3.11
- Java (para Allure)
- Allure CLI
- Playwright + Chromium
- Todas las dependencias del proyecto

**Tiempo estimado:** 3-5 minutos (primera vez)

---

## 3. Rebuild de la imagen Docker

Cuando hagas cambios en el código o dependencias, necesitarás reconstruir la imagen:

```bash
# Detener el server
docker compose down

# Reconstruir desde cero (sin caché)
docker compose build --no-cache

# Levantar el server
docker compose up -d
```

### Cuándo hacer rebuild

| Cambio | Rebuild necesario |
|--------|-------------------|
| Modificar `requirements.txt` | Sí |
| Cambiar archivos en `service_gateway/` | Sí |
| Cambiar archivos en `core/` | Sí |
| Cambiar archivos en `tests/` | No (se montan como volumen) |
| Modificar `Dockerfile` | Sí |
| Cambiar `.env` | No (se lee en runtime) |

### Build rápido (con caché)

Si solo cambiaste código Python (sin dependencias nuevas):

```bash
docker compose down
docker compose build  # Usa caché de capas anteriores
docker compose up -d
```

---

## 4. Ejecutar el Server FastAPI

### Levantar el server

```bash
# Ejecutar en background
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f
```

El server estará disponible en: `http://localhost:8000`

### Verificar que funciona

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Respuesta esperada:
# {"status":"healthy","service":"foxhound"}
```

### Swagger UI

Abrir en el navegador:
```
http://localhost:8000/docs
```

### Detener el server

```bash
docker compose down
```

---

## 4. Ejecutar tests vía API

### Ejecutar tests (POST)

```bash
curl -X POST http://localhost:8000/api/v1/tests/run \
  -H "Content-Type: application/json" \
  -d '{
    "team": "team1",
    "type": "api"
  }'
```

**Respuesta:**
```json
{
  "run_id": "abc123-def456",
  "status": "pending",
  "message": "Tests en cola de ejecución"
}
```

### Parámetros disponibles

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `team` | string | Sí | Nombre del equipo |
| `type` | string | Sí | `ui`, `api` o `all` |
| `feature` | string | No | Feature file específico |
| `tags` | string | No | Tags Behave (ej: `@smoke`) |

### Ejemplos de requests

**API tests:**
```bash
curl -X POST http://localhost:8000/api/v1/tests/run \
  -H "Content-Type: application/json" \
  -d '{"team": "team1", "type": "api"}'
```

**UI tests:**
```bash
curl -X POST http://localhost:8000/api/v1/tests/run \
  -H "Content-Type: application/json" \
  -d '{"team": "team1", "type": "ui"}'
```

**Feature específico:**
```bash
curl -X POST http://localhost:8000/api/v1/tests/run \
  -H "Content-Type: application/json" \
  -d '{"team": "team1", "type": "api", "feature": "posts.feature"}'
```

**Con tags:**
```bash
curl -X POST http://localhost:8000/api/v1/tests/run \
  -H "Content-Type: application/json" \
  -d '{"team": "team1", "type": "api", "tags": "@smoke"}'
```

---

## 5. Consultar estado de ejecución

```bash
curl http://localhost:8000/api/v1/tests/run/{run_id}
```

**Respuesta:**
```json
{
  "run_id": "abc123-def456",
  "team": "team1",
  "test_type": "api",
  "status": "completed",
  "exit_code": 0,
  "created_at": "2026-06-13T10:30:00",
  "completed_at": "2026-06-13T10:32:15"
}
```

### Estados posibles

| Estado | Descripción |
|--------|-------------|
| `pending` | En cola, esperando ejecución |
| `running` | Ejecutándose actualmente |
| `completed` | Finalizó exitosamente (exit_code = 0) |
| `failed` | Falló (exit_code != 0) |

---

## 6. Descargar reporte Allure

### Ver reporte HTML en navegador

```bash
# Abrir en navegador (muestra HTML directamente)
http://localhost:8000/api/v1/tests/run/{run_id}/report
```

### Descargar reporte HTML

```bash
# Forzar descarga del archivo HTML
curl -O "http://localhost:8000/api/v1/tests/run/{run_id}/report?download=true"
```

### Descargar datos raw (ZIP)

```bash
# Descargar ZIP con resultados Allure
curl -O "http://localhost:8000/api/v1/tests/run/{run_id}/report?format=raw"
```

### Parámetros del endpoint

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `format` | string | `html` | `html` o `raw` |
| `download` | bool | `false` | Forzar descarga del archivo |

### Abrir el reporte localmente

```bash
# Si descargaste el ZIP, descomprimir
unzip report-{run_id}.zip -d allure-results

# Abrir con Allure CLI (requiere instalación local)
allure serve allure-results
```

---

## 7. Ejecutar tests directamente en Docker (sin server)

Si solo quieres ejecutar tests sin levantar el server:

```bash
# API tests
docker compose -f docker-compose.test.yml run --rm tests \
  python run_tests.py -t team1 --type api

# UI tests
docker compose -f docker-compose.test.yml run --rm tests \
  python run_tests.py -t team1 --type ui

# Feature específico
docker compose -f docker-compose.test.yml run --rm tests \
  python run_tests.py -t team1 --type api -f posts.feature

# Con tags
docker compose -f docker-compose.test.yml run --rm tests \
  python run_tests.py -t team1 --tags @smoke
```

Los resultados se guardan en `./results/` (montado como volumen).

---

## 8. Webhook de GitHub Actions

El server expone un endpoint para recibir webhooks de GitHub:

```bash
POST /api/v1/webhooks/github
```

### Configurar en GitHub

1. Ir a Settings → Webhooks → Add webhook
2. Payload URL: `https://tu-servidor.com/api/v1/webhooks/github`
3. Content type: `application/json`
4. Secret: Configurar en `.env` como `GITHUB_WEBHOOK_SECRET`
5. Events: Seleccionar "Workflow runs"

### Seguridad

El webhook valida la firma HMAC SHA-256 en el header `X-Hub-Signature-256`.

---

## 9. Variables de entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `GITHUB_WEBHOOK_SECRET` | Secret para validar webhooks | `mi_secreto_seguro` |

Crear archivo `.env` en la raíz:
```bash
cp .env.example .env
# Editar con tus valores
```

---

## 10. Troubleshooting

### El server no levanta

```bash
# Ver logs
docker compose logs foxhound

# Verificar que el puerto está libre
netstat -ano | findstr :8000
```

### Los tests fallan con "ModuleNotFoundError"

Verificar que la imagen se construyó correctamente:
```bash
docker compose build --no-cache
```

### No se generan reportes Allure

Verificar que Allure CLI está instalado en la imagen:
```bash
docker compose run --rm tests allure --version
```

### Docker Compose no encuentra el archivo

Asegurarse de estar en la raíz del proyecto:
```bash
cd E:\Proyect-FoxHound
docker compose config
```

---

## 11. Arquitectura Docker

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Host                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────┐  ┌─────────────────────────┐  │
│  │   foxhound-api      │  │   foxhound-tests        │  │
│  │   (FastAPI)         │  │   (CLI runner)          │  │
│  │                     │  │                         │  │
│  │   Puerto: 8000      │  │   Ejecución única       │  │
│  │   Background        │  │   (on-demand)           │  │
│  └─────────┬───────────┘  └───────────┬─────────────┘  │
│            │                          │                │
│            ▼                          ▼                │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Volumen: ./results                  │   │
│  │              (Resultados Allure)                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 12. Comandos rápidos

```bash
# Build
docker compose build

# Server
docker compose up -d                    # Levantar
docker compose logs -f                  # Ver logs
docker compose down                     # Detener

# Tests via API
curl -X POST localhost:8000/api/v1/tests/run \
  -H "Content-Type: application/json" \
  -d '{"team":"team1","type":"api"}'

# Tests via Docker
docker compose -f docker-compose.test.yml run --rm tests \
  python run_tests.py -t team1 --type api
```
