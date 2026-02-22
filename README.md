# ZK-Skills

Colección de [Agent Skills](https://agentskills.io/) — formato abierto para extender agentes de IA con capacidades especializadas. Compatible con Cursor, Claude Code, Gemini CLI, VS Code, OpenAI Codex, y cualquier herramienta que soporte el estándar.

## Skills Disponibles

| Skill | Descripción | Categoría |
|-------|-------------|-----------|
| [browser-control](#browser-control) | Control completo de navegadores web con sistema de recipes | Automatización |
| [ssh-sheller](#ssh-sheller) | Gestión de servidores SSH, túneles y transferencia de archivos | DevOps |
| [desktop-commander](#desktop-commander) | Operaciones de sistema via Desktop Commander MCP | Sistema |
| [market-sentiment-analyzer](#market-sentiment-analyzer) | Análisis de sentimiento cripto desde feeds locales | Crypto / Data |
| [persistent-agents-orchestrator](#persistent-agents-orchestrator) | Orquestación de agentes persistentes en Docker + VPN | Infraestructura |
| [proton-suite](#proton-suite) | Automatización de Proton Mail/Calendar/Drive/Pass/Docs | Productividad |
| [protonvpn-wireguard](#protonvpn-wireguard) | Gestión de configs WireGuard desde panel Proton VPN | VPN / Seguridad |
| [wireguard-panel](#wireguard-panel) | Gestión de perfiles WireGuard desde panel web admin | VPN / Seguridad |

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

## Desktop Commander

Ejecuta operaciones de sistema (archivos, procesos, comandos) a través de Desktop Commander MCP como fallback cuando las herramientas nativas del agente son insuficientes.

[Ver documentación completa →](desktop-commander/SKILL.md)

---

## Market Sentiment Analyzer

Analiza sentimiento de mercado cripto leyendo feeds unificados de un gateway de datos local. Detecta tendencias, noticias y señales de Binance Square.

[Ver documentación completa →](market-sentiment-analyzer/SKILL.md)

---

## Persistent Agents Orchestrator

Orquesta agentes de IA persistentes como stacks Docker Compose (VPN + UI) con aislamiento de red estricto, egress solo por VPN y estado declarativo en JSON.

[Ver documentación completa →](persistent-agents-orchestrator/SKILL.md)

---

## Proton Suite

Automatiza Proton Mail, Calendar, Drive, Pass, Docs y Sheets mediante browser automation. Lectura/envío de emails, gestión de eventos, archivos y credenciales.

[Ver documentación completa →](proton-suite/SKILL.md)

---

## ProtonVPN WireGuard

Gestiona configs WireGuard desde el panel web de Proton VPN: crear, rotar, descargar, etiquetar y revocar perfiles.

[Ver documentación completa →](protonvpn-wireguard/SKILL.md)

---

## WireGuard Panel

Gestiona perfiles WireGuard desde un panel web admin genérico: crear, editar, revocar, descargar configs y QR.

[Ver documentación completa →](wireguard-panel/SKILL.md)

---

## Instalación

### Formato Agent Skills (estándar abierto)

Cada skill sigue la [especificación AgentSkills.io](https://agentskills.io/specification):

```
skill-name/
├── SKILL.md              # Documentación principal (frontmatter YAML + instrucciones)
├── scripts/              # Scripts ejecutables
│   └── *.py
├── references/           # Documentación adicional
│   └── *.md
├── assets/               # Archivos de ejemplo/configuración
│   └── *.yaml.example
└── recipes/              # (browser-control) Recipes guardados
    └── *.json
```

### Uso con cualquier agente compatible

```bash
# Clonar el repositorio
git clone https://github.com/ramgeart/zk-skills.git

# Copiar skills al directorio de tu agente
# Claude Code / Cursor / Gemini CLI / etc:
cp -r zk-skills/<skill-name> .agents/skills/
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
