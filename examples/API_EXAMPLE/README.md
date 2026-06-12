# API Example: Posts CRUD on JSONPlaceholder

Este ejemplo demuestra cómo automatizar pruebas de API usando Playwright APIRequestContext y Behave.

## API de prueba

- URL: `https://jsonplaceholder.typicode.com`
- Endpoints: `/posts`, `/posts/{id}`
- No requiere autenticación

## Estructura

```
API_EXAMPLE/
├── posts.feature              # Feature con escenarios Gherkin
├── steps/
│   └── posts_steps.py         # Step definitions
└── handlers/
    └── posts_handler.py       # Handler wrapper
```

## Cómo usar como base

1. Copia la carpeta `API_EXAMPLE/` a `api/teams/tu_equipo/`
2. Actualiza `api/resources/api_resources.ini` con tus endpoints
3. Crea un handler para tu dominio (ej: `users_handler.py`)
4. Crea los features y steps según tu API
5. Ejecuta: `python run_tests.py -t tu_equipo --type api`

## Patrones utilizados

- **Handler + Resources INI:** Config centralizada de endpoints
- **`@step` genérico:** Steps reutilizables
- **Allure attach:** Evidencia de request/response en cada step
- **Data tables:** Parámetros de request en tablas Gherkin
