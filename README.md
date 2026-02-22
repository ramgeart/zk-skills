# ZK-Skills

Colección de skills para [Kimi Code CLI](https://github.com/moonshot-ai/Kimi-Chat) - Capacidades especializadas para automatización y productividad.

## Skills Disponibles

| Skill | Descripción | Categoría |
|-------|-------------|-----------|
| [browser-control](#browser-control) | Control completo de navegadores web con sistema de recipes | Automatización |
| [ssh-sheller](#ssh-sheller) | Gestión de servidores SSH, túneles y transferencia de archivos | DevOps |

---

## Browser Control

Control completo de navegadores web usando Playwright. Automatiza cualquier interacción con sitios web e incluye un **sistema de Recipes** para guardar y reutilizar secuencias de acciones.

### Instalación

```bash
cd browser-control
pip install playwright
playwright install
```

### Características

- ✅ **30+ acciones**: navegación, clicks, formularios, screenshots, extracción de datos
- ✅ **Sistema de Recipes**: guarda y reutiliza secuencias de acciones
- ✅ **Múltiples navegadores**: Chromium, Firefox, WebKit
- ✅ **Variables dinámicas**: personaliza recipes con `{{variables}}`
- ✅ **Múltiples pestañas**: gestión completa de tabs
- ✅ **JavaScript**: ejecuta código en el navegador

### Uso Rápido

```bash
# Acción simple
python scripts/browser_controller.py --action navigate --url "https://ejemplo.com"
python scripts/browser_controller.py --action screenshot --full-page

# Sistema de recipes
python scripts/browser_controller.py --list-recipes
python scripts/browser_controller.py --create-recipe "mi-recipe" --steps-file steps.json
python scripts/browser_controller.py --run-recipe "mi-recipe" --var "email=test@mail.com"
```

### Acciones Disponibles

**Navegación**: `navigate`, `go_back`, `go_forward`, `reload`, `new_tab`, `close_tab`, `switch_tab`

**Interacción**: `click`, `fill`, `type`, `press_key`, `hover`, `focus`, `clear`, `check`, `select_option`

**Extracción**: `get_text`, `get_html`, `get_attribute`, `get_elements`, `screenshot`

**Espera**: `wait_for_selector`, `wait_for_load`, `sleep`

**JavaScript**: `evaluate`, `scroll`, `scroll_to_element`

### Ejemplo de Recipe

```json
{
  "name": "login-generico",
  "description": "Login automático",
  "variables": {"url": "", "username": "", "password": ""},
  "steps": [
    {"action": "navigate", "params": {"url": "{{url}}"}},
    {"action": "fill", "params": {"selector": "#user", "text": "{{username}}"}},
    {"action": "fill", "params": {"selector": "#pass", "text": "{{password}}"}},
    {"action": "click", "params": {"selector": "button[type='submit']"}},
    {"action": "wait_for_selector", "params": {"selector": ".dashboard"}}
  ]
}
```

[Ver documentación completa →](browser-control/SKILL.md)

---

## SSH Sheller

Ejecuta operaciones SSH (conexión, comandos remotos, túneles, transferencia SCP) con gestión de configuraciones en YAML.

### Características

- 🔑 **Gestión de servidores**: agrega, lista, elimina configuraciones
- 🔐 **Generación de claves**: crea claves ed25519 automáticamente
- 🚀 **Operaciones remotas**: exec, upload, download, tunnel
- 📁 **Configuración YAML**: almacena credenciales de forma organizada
- 🪟 **Cross-platform**: Windows, macOS, Linux

### Uso Rápido

```bash
# Primera vez - configuración interactiva
python scripts/ssh_sheller.py init
python scripts/ssh_sheller.py add-server

# Listar servidores
python scripts/ssh_sheller.py list-servers

# Conectar
python scripts/ssh_sheller.py mi-servidor connect

# Ejecutar comando
python scripts/ssh_sheller.py mi-servidor exec "ls -la /var/log"

# Crear túnel
python scripts/ssh_sheller.py mi-servidor tunnel --local 8080 --remote 80

# Transferir archivos
python scripts/ssh_sheller.py mi-servidor upload ./local.zip /remoto/
python scripts/ssh_sheller.py mi-servidor download /remoto/file.log ./
```

### Configuración

Crea `~/.ssh/sheller.yaml`:

```yaml
servers:
  web-prod:
    host: 192.168.1.100
    user: ubuntu
    key_file: ~/.ssh/id_ed25519
  
  db-server:
    host: db.example.com
    user: root
    port: 2222
    key_file: ~/.ssh/db_key
```

[Ver documentación completa →](ssh-sheller/SKILL.md)

---

## Instalación de Skills

### Para Kimi Code CLI

```bash
# Clonar el repositorio
git clone https://github.com/ramgeart/zk-skills.git

# Instalar skills en el directorio de Kimi
# Opción 1: Directorio de usuario
mkdir -p ~/.kimi/skills
cp -r zk-skills/browser-control ~/.kimi/skills/
cp -r zk-skills/ssh-sheller ~/.kimi/skills/

# Opción 2: Directorio del proyecto
mkdir -p .agents/skills
cp -r zk-skills/browser-control .agents/skills/
cp -r zk-skills/ssh-sheller .agents/skills/
```

### Estructura de un Skill

```
skill-name/
├── SKILL.md              # Documentación principal
├── scripts/              # Scripts ejecutables
│   └── *.py
├── references/           # Documentación adicional
│   └── *.md
├── assets/               # Archivos de ejemplo/configuración
│   └── *.yaml.example
└── recipes/              # (browser-control) Recipes guardados
    └── *.json
```

## Contribuir

1. Fork el repositorio
2. Crea un nuevo skill en un directorio separado
3. Incluye `SKILL.md` con documentación completa
4. Agrega el skill al índice de este README
5. Envía un Pull Request

## Licencia

MIT - Ver [LICENSE](LICENSE) para más detalles.

---

**ZK-Skills** - Automatización inteligente para desarrolladores
