# Guía Avanzada de Recipes

## ¿Qué son los Recipes?

Los recipes son secuencias de acciones de navegador guardadas en formato JSON que pueden ejecutarse múltiples veces. Son ideales para:

- Logins automáticos
- Reportes recurrentes
- Scraping periódico
- Flujos de trabajo repetitivos
- Pruebas automatizadas

## Estructura de un Recipe

```json
{
  "name": "nombre-recipe",
  "description": "Descripción del recipe",
  "created_at": "2024-01-15T10:30:00",
  "variables": {
    "var1": "valor_default",
    "var2": ""
  },
  "steps": [
    {
      "action": "nombre_accion",
      "params": {
        "param1": "valor",
        "param2": "{{variable}}"
      },
      "description": "Descripción del paso"
    }
  ]
}
```

## Acciones Disponibles en Recipes

Todas las acciones normales del browser controller están disponibles:

### Navegación
```json
{"action": "navigate", "params": {"url": "https://ejemplo.com"}}
{"action": "go_back"}
{"action": "go_forward"}
{"action": "reload"}
{"action": "new_tab", "params": {"url": "https://otro.com"}}
{"action": "close_tab"}
{"action": "switch_tab", "params": {"index": 0}}
```

### Interacción
```json
{"action": "click", "params": {"selector": "button#submit", "timeout": 5000}}
{"action": "fill", "params": {"selector": "input#email", "text": "usuario@mail.com"}}
{"action": "type", "params": {"selector": "input#search", "text": "query", "delay": 50}}
{"action": "press_key", "params": {"key": "Enter"}}
{"action": "hover", "params": {"selector": ".menu-item"}}
{"action": "clear", "params": {"selector": "input#email"}}
{"action": "check", "params": {"selector": "input#terms", "checked": true}}
```

### Dropdowns
```json
{"action": "select_option", "params": {"selector": "select#country", "value": "us"}}
{"action": "select_option", "params": {"selector": "select#country", "label": "United States"}}
{"action": "select_option", "params": {"selector": "select#country", "index": 0}}
```

### Esperas
```json
{"action": "wait_for_selector", "params": {"selector": ".loading", "timeout": 10000}}
{"action": "wait_for_load", "params": {"state": "networkidle"}}
{"action": "sleep", "params": {"seconds": 2}}
```

### Scroll
```json
{"action": "scroll", "params": {"direction": "down", "amount": 500}}
{"action": "scroll", "params": {"direction": "bottom"}}
{"action": "scroll", "params": {"direction": "top"}}
{"action": "scroll_to_element", "params": {"selector": "#footer"}}
```

### Extracción
```json
{"action": "get_text", "params": {"selector": ".article-content"}}
{"action": "get_html", "params": {"selector": "#main"}}
{"action": "get_attribute", "params": {"selector": "a#link", "attribute": "href"}}
{"action": "get_elements", "params": {"selector": ".product"}}
```

### JavaScript
```json
{"action": "evaluate", "params": {"script": "document.title"}}
{"action": "evaluate", "params": {"script": "window.scrollTo(0, 500)"}}
{"action": "evaluate", "params": {"script": "localStorage.getItem('token')"}}
```

### Capturas
```json
{"action": "screenshot", "params": {"full_page": true}}
{"action": "screenshot", "params": {"selector": "#chart"}}
```

### Viewport
```json
{"action": "set_viewport", "params": {"width": 1920, "height": 1080}}
{"action": "set_viewport", "params": {"width": 375, "height": 667}}
```

### Múltiples Pestañas
```json
{"action": "list_tabs"}
{"action": "switch_tab", "params": {"index": 1}}
{"action": "close_tab"}
```

## Variables

### Sintaxis

Usa `{{nombre_variable}}` en cualquier parámetro de tipo string:

```json
{
  "variables": {
    "username": "default_user",
    "password": ""
  },
  "steps": [
    {"action": "fill", "params": {"selector": "#user", "text": "{{username}}"}},
    {"action": "fill", "params": {"selector": "#pass", "text": "{{password}}"}}
  ]
}
```

### Valores por Defecto

```json
{
  "variables": {
    "url": "https://example.com",
    "timeout": "5000"
  }
}
```

### Ejecución con Variables

```bash
python scripts/browser_controller.py --run-recipe "mi-recipe" \
    --var "username=john" \
    --var "password=secret123" \
    --var "url=https://app.ejemplo.com"
```

## Ejemplos Completos

### Recipe: Login Genérico

```json
{
  "name": "login-generico",
  "description": "Login en cualquier sitio con variables",
  "variables": {
    "url": "",
    "user_selector": "input[name='email']",
    "pass_selector": "input[name='password']",
    "submit_selector": "button[type='submit']",
    "username": "",
    "password": "",
    "success_selector": ".dashboard"
  },
  "steps": [
    {
      "action": "navigate",
      "params": {"url": "{{url}}"},
      "description": "Navegar al login"
    },
    {
      "action": "wait_for_selector",
      "params": {"selector": "{{user_selector}}", "timeout": 10000},
      "description": "Esperar campo usuario"
    },
    {
      "action": "fill",
      "params": {"selector": "{{user_selector}}", "text": "{{username}}"},
      "description": "Ingresar usuario"
    },
    {
      "action": "fill",
      "params": {"selector": "{{pass_selector}}", "text": "{{password}}"},
      "description": "Ingresar contraseña"
    },
    {
      "action": "click",
      "params": {"selector": "{{submit_selector}}"},
      "description": "Enviar formulario"
    },
    {
      "action": "wait_for_selector",
      "params": {"selector": "{{success_selector}}", "timeout": 10000},
      "description": "Esperar login exitoso"
    },
    {
      "action": "screenshot",
      "params": {"full_page": true},
      "description": "Capturar resultado"
    }
  ]
}
```

### Recipe: Scrolling Infinito

```json
{
  "name": "scroll-infinito",
  "description": "Hacer scroll hasta cargar todo el contenido",
  "variables": {
    "url": "",
    "scrolls": "5",
    "delay": "2"
  },
  "steps": [
    {
      "action": "navigate",
      "params": {"url": "{{url}}"},
      "description": "Abrir página"
    },
    {
      "action": "evaluate",
      "params": {"script": "Array.from({length: {{scrolls}}}, (_, i) => setTimeout(() => window.scrollTo(0, document.body.scrollHeight), i * {{delay}} * 1000))"},
      "description": "Scroll múltiple"
    },
    {
      "action": "sleep",
      "params": {"seconds": "{{scrolls}} * {{delay}} + 2"},
      "description": "Esperar carga"
    },
    {
      "action": "screenshot",
      "params": {"full_page": true},
      "description": "Capturar todo"
    }
  ]
}
```

### Recipe: Extraer Datos de Tabla

```json
{
  "name": "extraer-tabla",
  "description": "Extraer datos de una tabla HTML",
  "variables": {
    "url": "",
    "table_selector": "table.data",
    "filename": "datos.json"
  },
  "steps": [
    {
      "action": "navigate",
      "params": {"url": "{{url}}"},
      "description": "Abrir página"
    },
    {
      "action": "wait_for_selector",
      "params": {"selector": "{{table_selector}}"},
      "description": "Esperar tabla"
    },
    {
      "action": "evaluate",
      "params": {
        "script": "() => { const rows = document.querySelectorAll('{{table_selector}} tr'); return Array.from(rows).map(r => Array.from(r.cells).map(c => c.innerText)); }"
      },
      "description": "Extraer datos"
    }
  ]
}
```

## Mejores Prácticas

### 1. Usar Descripciones

Siempre incluye descripciones para facilitar el debugging:

```json
{
  "action": "click",
  "params": {"selector": "#submit"},
  "description": "Enviar formulario de login"
}
```

### 2. Manejar Timeouts

Aumenta timeouts para operaciones lentas:

```json
{
  "action": "wait_for_selector",
  "params": {"selector": ".slow-loading", "timeout": 30000}
}
```

### 3. Capturas en Pasos Críticos

```json
{
  "action": "click",
  "params": {"selector": "#submit"}
},
{
  "action": "screenshot",
  "params": {},
  "description": "Verificar resultado del click"
}
```

### 4. Esperas Apropiadas

```json
// ❌ Mal: click inmediato
{"action": "navigate", "params": {"url": "https://ejemplo.com"}}
{"action": "click", "params": {"selector": "#btn"}}

// ✅ Bien: esperar carga
{"action": "navigate", "params": {"url": "https://ejemplo.com"}}
{"action": "wait_for_load", "params": {"state": "networkidle"}}
{"action": "click", "params": {"selector": "#btn"}}
```

## Gestión de Recipes

### Crear
```bash
# Desde archivo
python scripts/browser_controller.py --create-recipe "nombre" --steps-file steps.json

# Desde string JSON
python scripts/browser_controller.py --create-recipe "nombre" --steps '[{...}]'

# Con descripción y variables
python scripts/browser_controller.py --create-recipe "nombre" \
    --description "Mi descripción" \
    --steps-file steps.json \
    --variables '{"var1":"default"}'
```

### Listar
```bash
python scripts/browser_controller.py --list-recipes
```

### Ver
```bash
python scripts/browser_controller.py --show-recipe "nombre"
```

### Ejecutar
```bash
# Básico
python scripts/browser_controller.py --run-recipe "nombre"

# Con variables
python scripts/browser_controller.py --run-recipe "nombre" \
    --var "email=test@mail.com" \
    --var "password=123456"

# Con navegador visible
python scripts/browser_controller.py --run-recipe "nombre" --headless false
```

### Eliminar
```bash
python scripts/browser_controller.py --delete-recipe "nombre"
```

## Ubicación de Recipes

Los recipes se guardan en:
```
browser-control/
└── recipes/
    ├── nombre-recipe.json
    └── otro-recipe.json
```

## Troubleshooting

### Recipe no encontrado
- Verificar nombre exacto
- Usar `--list-recipes` para ver disponibles
- Nombres se sanitizan: espacios → guiones, minúsculas

### Variables no reemplazadas
- Verificar sintaxis `{{variable}}`
- Asegurar que la variable esté definida
- Verificar que el parámetro sea string

### Timeout en ejecución
- Aumentar `timeout` en los params
- Agregar `sleep` entre pasos
- Verificar selectores con `--show-recipe`

### Paso falla pero debería funcionar
- Agregar `screenshot` antes del paso
- Verificar con `--headless false`
- Revisar descripción del error en output
