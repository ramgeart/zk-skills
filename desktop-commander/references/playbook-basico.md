# Playbook básico — Desktop Commander MCP

## Métodos expuestos (26)

### Configuración
- `get_config`
- `set_config_value`

### Terminal / procesos
- `start_process`
- `interact_with_process`
- `read_process_output`
- `force_terminate`
- `list_sessions`
- `list_processes`
- `kill_process`

### Archivos / filesystem
- `read_file`
- `read_multiple_files`
- `write_file`
- `write_pdf`
- `create_directory`
- `list_directory`
- `move_file`
- `start_search`
- `get_more_search_results`
- `stop_search`
- `list_searches`
- `get_file_info`

### Edición
- `edit_block`

### Analítica / soporte
- `get_usage_stats`
- `get_recent_tool_calls`
- `give_feedback_to_desktop_commander`
- `get_prompts`

---

## Flujo recomendado (rápido y seguro)

1. **Inspeccionar primero**
   - `get_config`
   - `list_directory` / `get_file_info`
2. **Operar en pequeño**
   - lectura: `read_file`
   - cambios puntuales: `edit_block`
3. **Mutaciones con verificación inmediata**
   - `write_file` / `move_file` / `create_directory`
   - luego `read_file` o `list_directory` para confirmar
4. **Procesos largos en sesiones**
   - `start_process` → `read_process_output` / `interact_with_process`
   - cerrar con `force_terminate` o `kill_process` si se cuelga
5. **Búsquedas grandes en streaming**
   - `start_search` → `get_more_search_results` → `stop_search`

---

## Recetas básicas por tipo de tarea

### 1) Explorar proyecto
- `list_directory` (depth 2)
- `read_multiple_files` (README, package.json, entrypoints)
- `start_search` por símbolos clave

### 2) Editar archivo sin romper
- `read_file`
- `edit_block` (bloques pequeños)
- `read_file` de validación

### 3) Ejecutar comando y seguir salida
- `start_process` (comando)
- `read_process_output` (poll)
- `interact_with_process` si pide input
- `force_terminate` al terminar

### 4) Buscar y refactor rápido
- `start_search` (patrón)
- `get_more_search_results` hasta completar
- `edit_block` por archivo
- `read_file` para verificar diff

### 5) Auditoría de estado
- `list_sessions` y `list_processes`
- `get_recent_tool_calls`
- `get_usage_stats`

---

## Guardrails

- Confirmar antes de acciones destructivas (`move_file` sobre rutas críticas, sobrescrituras masivas, `kill_process`).
- Evitar tocar fuera de rutas solicitadas.
- No exponer secretos en salida.
- Si falla un método, reintentar **una vez** y luego cambiar de estrategia (no loops ciegos).
