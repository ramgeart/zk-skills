---
name: browser-control
description: Control completo de navegadores web para automatización, scraping, testing y tareas interactivas. Use cuando Kimi necesite navegar sitios web, hacer clic, llenar formularios, tomar screenshots, extraer datos, ejecutar JavaScript, manejar múltiples pestañas, o realizar cualquier acción en un navegador. Soporta Chromium, Firefox y WebKit. INCLUYE SISTEMA DE RECIPES para guardar y reutilizar secuencias de acciones.
---

# Browser Control

Control completo de navegadores web usando Playwright. Permite automatizar cualquier interacción con sitios web e incluye un **sistema de Recipes** para guardar y reutilizar secuencias de acciones.

## Instalación

```bash
pip install playwright
playwright install
```

## Uso Básico

```bash
# Acción simple
python scripts/browser_controller.py --action navigate --url "https://ejemplo.com"

# Usar sistema de recipes
python scripts/browser_controller.py --list-recipes
python scripts/browser_controller.py --run-recipe "nombre-recipe"
```

## Acciones Disponibles

### Navegación
- `navigate` - Navegar a URL
- `go_back` - Retroceder en historial
- `go_forward` - Avanzar en historial  
- `reload` - Recargar página
- `new_tab` - Nueva pestaña
- `close_tab` - Cerrar pestaña
- `switch_tab` - Cambiar pestaña
- `list_tabs` - Listar pestañas

### Interacción
- `click` - Clic en elemento
- `fill` - Llenar campo
- `type` - Escribir texto (simula humano)
- `press_key` - Presionar tecla especial
- `hover` - Hover sobre elemento
- `focus` - Enfocar elemento
- `clear` - Limpiar campo
- `check` - Marcar/desmarcar checkbox
- `select_option` - Seleccionar opción dropdown

### Espera
- `wait_for_selector` - Esperar elemento
- `wait_for_load` - Esperar carga de página
- `sleep` - Pausar ejecución

### Scroll
- `scroll` - Scroll direccional
- `scroll_to_element` - Scroll hasta elemento

### Extracción de Datos
- `get_text` - Obtener texto
- `get_html` - Obtener HTML
- `get_attribute` - Obtener atributo
- `get_elements` - Listar elementos

### JavaScript
- `evaluate` - Ejecutar código JS

### Capturas
- `screenshot` - Tomar screenshot

### Otras
- `set_viewport` - Cambiar tamaño ventana
- `handle_dialog` - Manejar diálogos

## Sistema de Recipes 🍳

Los **Recipes** son secuencias de acciones guardadas que se pueden reutilizar. Perfectos para tareas repetitivas.

### Comandos de Recipes

| Comando | Descripción |
|---------|-------------|
| `--list-recipes` | Listar todos los recipes guardados |
| `--create-recipe "nombre"` | Crear un nuevo recipe |
| `--run-recipe "nombre"` | Ejecutar un recipe |
| `--show-recipe "nombre"` | Mostrar contenido de un recipe |
| `--delete-recipe "nombre"` | Eliminar un recipe |

### Crear un Recipe

```bash
# Crear recipe desde archivo JSON
python scripts/browser_controller.py --create-recipe "buscar-en-google" \
    --description "Buscar en Google" \
    --steps-file steps.json

# Crear recipe desde línea de comandos
python scripts/browser_controller.py --create-recipe "ejemplo" \
    --description "Recipe de ejemplo" \
    --steps '[{"action":"navigate","params":{"url":"https://example.com"}}]'
```

### Formato de Steps (JSON)

```json
[
  {
    "action": "navigate",
    "params": {"url": "https://pass.proton.me"},
    "description": "Ir a Proton Pass"
  },
  {
    "action": "wait_for_selector",
    "params": {"selector": "input[type='email']", "timeout": 10000},
    "description": "Esperar campo email"
  },
  {
    "action": "fill",
    "params": {"selector": "input[type='email']", "text": "{{email}}"},
    "description": "Ingresar email"
  },
  {
    "action": "click",
    "params": {"selector": "button[type='submit']"},
    "description": "Continuar"
  },
  {
    "action": "screenshot",
    "params": {"full_page": true},
    "description": "Capturar resultado"
  }
]
```

### Variables en Recipes

Usa `{{variable}}` para valores dinámicos:

```json
{
  "variables": {
    "email": "usuario@ejemplo.com",
    "password": ""
  },
  "steps": [
    {"action": "fill", "params": {"selector": "#email", "text": "{{email}}"}},
    {"action": "fill", "params": {"selector": "#password", "text": "{{password}}"}}
  ]
}
```

Ejecutar con variables:
```bash
python scripts/browser_controller.py --run-recipe "login" \
    --var "email=usuario@mail.com" \
    --var "password=secreto123"
```

### Ejemplo: Guardar Registro en Proton Pass

```bash
# Crear el recipe
cat > proton-pass.json << 'EOF'
{
  "variables": {
    "service": "",
    "username": "",
    "password": "",
    "note": ""
  },
  "steps": [
    {
      "action": "navigate",
      "params": {"url": "https://pass.proton.me"},
      "description": "Abrir Proton Pass"
    },
    {
      "action": "wait_for_load",
      "params": {"state": "networkidle"},
      "description": "Esperar carga"
    },
    {
      "action": "click",
      "params": {"selector": "button[data-testid='new-item']"},
      "description": "Nuevo item"
    },
    {
      "action": "click",
      "params": {"selector": "[data-testid='login']"},
      "description": "Seleccionar Login"
    },
    {
      "action": "wait_for_selector",
      "params": {"selector": "input[name='name']"},
      "description": "Esperar formulario"
    },
    {
      "action": "fill",
      "params": {"selector": "input[name='name']", "text": "{{service}}"},
      "description": "Nombre del servicio"
    },
    {
      "action": "fill",
      "params": {"selector": "input[name='username']", "text": "{{username}}"},
      "description": "Usuario"
    },
    {
      "action": "fill",
      "params": {"selector": "input[name='password']", "text": "{{password}}"},
      "description": "Contraseña"
    },
    {
      "action": "fill",
      "params": {"selector": "textarea[name='note']", "text": "{{note}}"},
      "description": "Nota"
    },
    {
      "action": "click",
      "params": {"selector": "button[type='submit']"},
      "description": "Guardar"
    },
    {
      "action": "wait_for_selector",
      "params": {"selector": ".success-message", "timeout": 5000},
      "description": "Confirmar guardado"
    }
  ]
}
EOF

python scripts/browser_controller.py --create-recipe "guardar-en-proton-pass" \
    --description "Guardar un nuevo registro en Proton Pass" \
    --steps-file proton-pass.json \
    --variables '{"service":"","username":"","password":"","note":""}'
```

Ejecutarlo:
```bash
python scripts/browser_controller.py --run-recipe "guardar-en-proton-pass" \
    --var "service=GitHub" \
    --var "username=miusuario" \
    --var "password=miclavesegura123" \
    --var "note=Cuenta principal"
```

### Listar Recipes

```bash
python scripts/browser_controller.py --list-recipes
```

Salida:
```json
{
  "success": true,
  "action": "list_recipes",
  "data": {
    "count": 2,
    "recipes": [
      {
        "name": "guardar-en-proton-pass",
        "description": "Guardar un nuevo registro en Proton Pass",
        "steps_count": 11,
        "variables": ["service", "username", "password", "note"]
      }
    ]
  }
}
```

## Parámetros Comunes

| Parámetro | Descripción | Default |
|-----------|-------------|---------|
| `--action, -a` | Acción a ejecutar | - |
| `--url` | URL para navegar | - |
| `--selector, -s` | Selector CSS | - |
| `--text, -t` | Texto a escribir | - |
| `--key` | Tecla especial | - |
| `--timeout` | Timeout ms | 5000 |
| `--full-page` | Screenshot completo | false |
| `--headless` | Modo sin interfaz | true |
| `--browser` | Tipo navegador | chromium |

## Ejemplos

### Buscar en Google
```bash
python scripts/browser_controller.py -a navigate --url "https://google.com"
python scripts/browser_controller.py -a fill -s "textarea[name='q']" -t "python tutorial"
python scripts/browser_controller.py -a press_key --key "Enter"
python scripts/browser_controller.py -a wait_for_load
python scripts/browser_controller.py -a screenshot
```

### Extraer texto de elementos
```bash
python scripts/browser_controller.py -a navigate --url "https://news.ycombinator.com"
python scripts/browser_controller.py -a get_text -s ".titleline > a"
```

### Login Automático como Recipe
```bash
# Crear recipe
cat > login.json << 'EOF'
[
  {"action": "navigate", "params": {"url": "{{url}}"}},
  {"action": "fill", "params": {"selector": "input[name='email']", "text": "{{email}}"}},
  {"action": "fill", "params": {"selector": "input[name='password']", "text": "{{password}}"}},
  {"action": "click", "params": {"selector": "button[type='submit']"}},
  {"action": "wait_for_selector", "params": {"selector": ".dashboard", "timeout": 10000}},
  {"action": "screenshot", "params": {"full_page": true}}
]
EOF

python scripts/browser_controller.py --create-recipe "login-generico" \
    --description "Login automático en cualquier sitio" \
    --steps-file login.json

# Ejecutar
python scripts/browser_controller.py --run-recipe "login-generico" \
    --var "url=https://app.ejemplo.com/login" \
    --var "email=usuario@mail.com" \
    --var "password=secreto123"
```

## Referencias

- `references/playwright_selectors.md` - Guía completa de selectores
- `references/best_practices.md` - Patrones avanzados de automatización
- `references/recipes.md` - Guía avanzada de recipes con ejemplos
