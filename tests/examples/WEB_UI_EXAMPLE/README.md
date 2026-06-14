# Web UI Example: Login on SauceDemo

Este ejemplo demuestra cómo automatizar un flujo de login usando Playwright y Behave.

## Site de prueba

- URL: `https://www.saucedemo.com/`
- Credenciales válidas: `standard_user` / `secret_sauce`

## Estructura

```
WEB_UI_EXAMPLE/
├── login.feature          # Feature con escenarios Gherkin
├── steps/
│   └── login_steps.py     # Step definitions
└── pages/
    └── login_page.py      # Page Object
```

## Cómo usar como base

1. Copia la carpeta `WEB_UI_EXAMPLE/` a `tests/webui/teams/tu_equipo/`
2. Renombra los archivos según tu dominio
3. Modifica los selectores en el Page Object
4. Actualiza los steps según tu lógica de negocio
5. Ejecuta: `python run_tests.py -t tu_equipo --type ui`

## Patrones utilizados

- **Page Object Model (POM):** Separación de selectores y lógica de página
- **`@step` genérico:** Steps reutilizables sin atar a Given/When/Then
- **Allure attach:** Cada step genera evidencia en el reporte
